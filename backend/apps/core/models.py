from django.db import models
from taggit.managers import TaggableManager
from django.utils.functional import cached_property
from django.utils.duration import _get_duration_components  # type: ignore
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title


class RecurrenceSeries(models.Model):
    # Raw RFC‑5545 string, e.g. "FREQ=DAILY;INTERVAL=2"
    recurrence_rule = models.TextField(
        blank=True, null=True, help_text="RRULE string (RFC-5545)."
    )


class Task(models.Model):
    BACKLOG = "BACKLOG"
    BRAINDUMP = "BRAINDUMP"
    ON_BOARD = "ON_BOARD"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
    ON_CAL = "ON_CAL"
    TASK_STATUS_CHOICES = (
        (BACKLOG, "Backlog"),
        (BRAINDUMP, "Brain Dump"),
        (ON_BOARD, "On Board"),
        (ON_CAL, "ON CALENDAR"),
        (COMPLETED, "Completed"),
        (ARCHIVED, "Archived"),
    )
    # when saving task from frontend, we will generate a random id for it
    # this id will be used to identify the task in frontend
    frontend_id = models.PositiveBigIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS_CHOICES,
        default=BRAINDUMP,
        help_text="Status of the task.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.DurationField(blank=True, null=True)
    # start_at, end_at are used for calendar events & task location on kanban board
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    tags = TaggableManager(blank=True)
    project = models.ForeignKey(
        Project,
        related_name="tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    recurrence_series = models.ForeignKey(
        RecurrenceSeries,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    # keep a record of changes to this model
    history = HistoricalRecords()

    class Meta:
        ordering = ["start_at", "order"]

    def __str__(self):
        return self.title

    @cached_property
    def get_duration_display(self):
        if self.duration:
            day, hours, minutes, _, _ = _get_duration_components(self.duration)
            final_str = ""
            if hours > 0:
                final_str += f"{hours}h "
            if minutes > 0:
                final_str += f"{minutes}m"
            if day > 0:
                final_str = f"{day}d " + final_str
            return final_str.strip()
        return None
