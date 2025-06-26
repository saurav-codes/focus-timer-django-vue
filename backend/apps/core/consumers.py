import json
import logging
from channels.consumer import database_sync_to_async
from django.http import HttpRequest
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .selectors import get_filtered_tasks_for_user_serialized
from .services import TaskService

# Set up logger with module name for better debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TasksConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer for sending/recieving Task data. sending data
    must be serialized using `TaskSerializer`
    """

    # -- Utility helpers --------------------------------------------------
    def _prepare_req_obj_with_user(self, user):
        request = HttpRequest()
        request.user = user
        return request

    # -- Action registry --------------------------------------------------
    ACTION_HANDLERS: dict[str, str] = {
        "fetch_tasks": "handle_fetch_tasks",
        "create_task": "handle_create_task",
        "delete_task": "handle_delete_task",
        "update_task": "handle_update_task",
        "update_task_order": "handle_update_task_order",
        "assign_project": "handle_assign_project",
        "turn_off_repeat": "handle_turn_off_repeat",
        "toggle_completion": "handle_toggle_completion",
        "refresh_for_rec_task": "refresh_for_rec_task",  # used by celery task to send update to client
        "full_refresh": "full_refresh",
    }

    # -- Connection lifecycle --------------------------------------------
    async def connect(self):
        try:
            self.user = self.scope["user"]

            if self.user and self.user.is_authenticated:
                await self.accept()

                # join per-user broadcast group so background tasks can push updates
                group_name = f"tasks_user_{self.user.id}"
                await self.channel_layer.group_add(group_name, self.channel_name)  # type:ignore

                self.task_service = TaskService(self.user)
                self.request = self._prepare_req_obj_with_user(self.user)

                await self.send_json({"type": "connected"})
                logger.info(
                    f"WebSocket connection established for user: {self.user.id}"
                )
            else:
                logger.warning("WebSocket connection rejected: Unauthenticated user")
                await self.close(code=401, reason="Authentication required")

        except Exception as e:
            logger.error(f"Error in WebSocket connect: {str(e)}", exc_info=True)
            await self.close(code=1011, reason=f"Server error: {str(e)}")

    async def disconnect(self, code):
        if getattr(self, "user", None) and self.user.is_authenticated:
            group_name = f"tasks_user_{self.user.id}"
            await self.channel_layer.group_discard(group_name, self.channel_name)  # type:ignore
        await super().disconnect(code)

    async def receive_json(self, content, **kwargs):
        try:
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

            handler_name = self.ACTION_HANDLERS.get(action)
            if not hasattr(self, handler_name):  # type:ignore
                logger.warning(f"No handler found for action: {action}")
                await self.send_json(
                    {
                        "type": "error",
                        "error": "Invalid action",
                    }
                )
                return

            handler = getattr(self, handler_name)  # type:ignore
            payload = content.get("payload", {})

            try:
                response = await handler(payload)
                await self.send_json(response)
            except Exception as e:
                logger.error(
                    f"Error handling action '{action}': {str(e)}", exc_info=True
                )
                await self.send_json(
                    {
                        "type": "error",
                        "error": f"Error processing {action}",
                        "details": str(e),
                    }
                )

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await self.send_json({"error": "Invalid JSON received"})

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await self.send_json({"error": "An error occurred"})

    async def handle_fetch_tasks(self, filter_data):
        try:
            tasks_data = await get_filtered_tasks_for_user_serialized(
                self.user.id, filter_data
            )
            return {"type": "tasks.list", "data": tasks_data}

        except Exception as e:
            logger.error(
                f"[WebSocket] Error in handle_fetch_tasks: {str(e)}", exc_info=True
            )
            return {
                "type": "error",
                "error": "Failed to fetch tasks",
                "details": str(e),
            }

    @database_sync_to_async
    def _create_task(self, payload):
        serialized_data, is_created = self.task_service.create_task(
            payload, self.request
        )
        if is_created:
            return {"type": "task.created", "data": serialized_data}
        return {
            "type": "error",
            "error": "Failed to create task",
            "details": serialized_data,
        }

    async def handle_create_task(self, payload):
        return await self._create_task(payload)

    @database_sync_to_async
    def _delete_task(self, task_id):
        task_data = self.task_service.delete_task(task_id)
        return {"type": "task.deleted", "id": task_data.get("id")}

    async def handle_delete_task(self, task_id):
        logger.info(f"Deleting task: task_id={task_id} by user_id={self.user.id}")
        response = await self._delete_task(task_id)
        await self.send_json(response)

    @database_sync_to_async
    def _update_task_order(self, tasks):
        self.task_service.update_task_order(tasks)

    async def handle_update_task_order(self, tasks):
        logger.info(
            f"websocket - Bulk update order by user_id={self.user.id} for task_ids={[t['id'] for t in tasks]}"
        )
        await self._update_task_order(tasks)

    @database_sync_to_async
    def _update_task(self, task_data):
        updated_task, is_updated = self.task_service.update_task(task_data)
        if is_updated:
            return {"type": "task.updated", "data": updated_task}
        return {
            "type": "error",
            "error": "Failed to update task",
            "details": updated_task,
        }

    async def handle_update_task(self, task_data):
        response_data = await self._update_task(task_data)
        await self.send_json(response_data)

    @database_sync_to_async
    def _assign_project(self, task_id, project_id):
        task_data = self.task_service.assign_project_to_task(task_id, project_id)
        return {"type": "task.updated", "data": task_data}

    async def handle_assign_project(self, data):
        task_id, project_id = data["task_id"], data["project_id"]
        response_data = await self._assign_project(task_id, project_id)
        await self.send_json(response_data)

    @database_sync_to_async
    def _turn_off_repeat(self, task_id):
        self.task_service.turn_off_repeat(task_id)
        return {"type": "full_refresh"}

    async def handle_turn_off_repeat(self, task_id):
        response_data = await self._turn_off_repeat(task_id)
        await self.send_json(response_data)

    @database_sync_to_async
    def _toggle_completion(self, task_id):
        updated_task = self.task_service.toggle_task_completion(task_id)
        return {
            "type": "task.updated",
            "data": updated_task,
        }

    async def handle_toggle_completion(self, task_id):
        response_data = await self._toggle_completion(task_id)
        await self.send_json(response_data)

    # -----------------------------------------------------------------
    # to be called by external logic like from tasks, models, etc.
    # -----------------------------------------------------------------
    async def full_refresh(self, data):
        await self.send_json(data)

    async def refresh_for_rec_task(self, payload):
        await self.send_json({"type": "task.refresh_for_rec", "data": payload})
