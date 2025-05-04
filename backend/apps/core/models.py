from django.db import models
from taggit.managers import TaggableManager
from django.utils.functional import cached_property
from django.utils.duration import _get_duration_components
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


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    planned_duration = models.DurationField(blank=True, null=True)
    # column_date is used for tracking the location of task in the kanban board column
    column_date = models.DateTimeField(blank=True, null=True)
    # start_at, end_at are used for calendar events
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    ############### recuring task data ###############
    # 1) Raw RFC‑5545 string, e.g. "FREQ=DAILY;INTERVAL=2"
    recurrence_rule = models.TextField(
        blank=True,
        null=True,
        help_text="RRULE string (RFC-5545)."
    )
    # 2) Points at the “template” task
    recurrence_parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='recurrence_children'
    )

    # timezone info will be fetched based on where user is logged in from
    # so we can fetch this info from user's browser
    # we may need to handle it differently if user is let's say travelling
    # because he will add the task in diff timezones.
    tags = TaggableManager(blank=True)
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']

    @cached_property
    def get_planned_duration_display(self):
        if self.planned_duration:
            _, hours, minutes, _, _= _get_duration_components(self.planned_duration)
            final_str = ""
            if hours > 0:
                final_str += f"{hours}h "
            if minutes > 0:
                final_str += f"{minutes}m"
            return final_str.strip()
        return None

    @cached_property
    def is_original(self):
        """
        Check if the task is an original task (not a recurrence child).
        """
        return self.recurrence_parent is None

