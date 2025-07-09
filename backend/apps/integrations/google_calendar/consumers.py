from datetime import datetime, timezone as dt_tz, timedelta
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.consumer import database_sync_to_async
import uuid
from django.urls import reverse
from .utils import build_calendar_service, format_event_for_fullcalendar
from .models import GoogleCalendarCredentials

import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GoogleCalendarConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer dedicated to Google-Calendar events for a single user.

    • Fetches the latest events immediately on connect and pushes them to the client.
    • Joins a per-user channel-layer group (``gcal_user_<id>``) so that server-side
      code/webhooks can fan-out incremental updates via ``notify_frontend``.
    """

    async def connect(self):  # type: ignore
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(code=401)
            return

        # accept connection & join group
        await self.accept()
        self.group_name = f"gcal_user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)  # type: ignore

        # send connected ack
        await self.send_json({"type": "connected"})

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)  # type: ignore
        await super().disconnect(code)

    async def receive_json(self, content, **kwargs):
        action = content.get("action")

        if not action:
            logger.warning("No action specified in WebSocket message")
            await self.send_json(
                {
                    "type": "error",
                    "error": "No action specified",
                    "details": 'The message must contain an "action" field',
                }
            )
            return
        if action == "fetch_gcal_task_from_dt":
            payload = content.get("payload")
            date_iso_str = payload.get("date_iso_str")
            if not date_iso_str:
                return await self.send_json(
                    {"type": "error", "error": "no `date_iso_str` found"}
                )
            resp = await self.fetch_cal_taks_from_dt(date_iso_str)
            return resp

    async def fetch_cal_taks_from_dt(self, date_str: str):
        # validate incoming date string is exactly YYYY-MM-DD
        if not isinstance(date_str, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", date_str
        ):
            await self.send_json(
                {"type": "error", "error": "Invalid date format, expected YYYY-MM-DD"}
            )
            return
        # parse the date value
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            await self.send_json({"type": "error", "error": "Invalid date value"})
            return

        try:
            events = await self._fetch_events(date_str)
            # await self._start_push_subscription()
            # TODO: make sure we only subscribe to notification
            # when already there not a subscription
            # we can use cred obj to store notific related data to avoid duplicate watch
            await self.send_json({"type": "gcal.events", "data": events})
        except Exception as exc:
            logger.error(
                "Failed to fetch gcal events for user %s: %s",
                self.user.id,
                exc,
                exc_info=True,
            )
            await self.send_json(
                {"type": "error", "error": "Unable to fetch calendar events"}
            )

    # ------------------------------------------------------------------
    #   Group message handlers (called via channel_layer.group_send)
    # ------------------------------------------------------------------
    async def gcal_event(self, event):
        """Forward a calendar event/update coming from server-side code."""
        await self.send_json(event)

    # ------------------------------------------------------------------
    #   Helpers
    # ------------------------------------------------------------------
    @database_sync_to_async
    def _fetch_events(self, date_str: str):
        """Synchronously fetch Google-Calendar events & return FullCalendar-ready list."""
        # Get stored credentials
        creds_obj = GoogleCalendarCredentials.objects.filter(user=self.user).first()
        if not creds_obj:
            return []

        creds = creds_obj.get_credentials()
        if isinstance(creds, dict):
            # token problem; surface error through websocket
            raise ValueError(
                creds.get(
                    "error",
                    "Invalid credentials. Please disconnect & re-connect your google calendar",
                )
            )

        service = build_calendar_service(creds)
        calendar_id = creds_obj.calendar_id or "primary"

        today_datetime = datetime.fromisoformat(date_str)
        today_datetime = today_datetime.replace(tzinfo=dt_tz.utc)
        # we are fetching event 1 day before - after 1 days so if user is travelling
        # and there were events created before the current tz then it will fetch all
        # those events too.
        yesterday = today_datetime - timedelta(days=1, hours=2)
        tmrw = today_datetime + timedelta(days=1)
        filter_params = {
            "calendarId": calendar_id,
            "timeMin": yesterday.isoformat(),
            "timeMax": tmrw.isoformat(),
        }
        events_result = service.events().list(**filter_params).execute()
        raw_events = events_result.get("items", [])
        next_sync_token = events_result.get("nextSyncToken")
        if next_sync_token:
            creds_obj.next_sync_token = next_sync_token
            creds_obj.last_sync_params = filter_params  # type: ignore

        return [format_event_for_fullcalendar(ev) for ev in raw_events]

    async def _start_push_subscription(self):
        """
        Start a Google Calendar watch channel for this user's 'today' events.
        """
        try:
            await self._sync_start_watch()
        except Exception as e:
            logger.error(f"Failed to start gcal push subscription: {e}", exc_info=True)

    @database_sync_to_async
    def _sync_start_watch(self):
        # Get credentials
        creds_obj = GoogleCalendarCredentials.objects.filter(user=self.user).first()
        if not creds_obj:
            return
        creds = creds_obj.get_credentials()
        if isinstance(creds, dict):
            return
        service = build_calendar_service(creds)
        # TODO: extract service init to self.service
        # Prepare watch request: reuse saved channel_id if present
        channel_id = str(uuid.uuid4())
        webhook_url = "https://tymr.online" + reverse(
            "google_calendar:google_calendar_webhook"
        )
        body = {
            "id": channel_id,
            "type": "web_hook",
            "address": webhook_url,
        }
        try:
            service.events().watch(
                calendarId=creds_obj.calendar_id or "primary",
                body=body,
            ).execute()
            # Save channel_id back to model if new
            if creds_obj.channel_id != channel_id:
                creds_obj.channel_id = channel_id
                creds_obj.save(update_fields=["channel_id"])
        except Exception as e:
            logger.error(f"Error registering gcal watch channel: {e}", exc_info=True)
