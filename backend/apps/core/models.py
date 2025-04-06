from django.db import models
from taggit.managers import TaggableManager


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # column_date is used for tracking the location of task in the kanban board column
    column_date = models.DateTimeField(blank=True, null=True)
    # start_at, end_at are used for calendar events
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    # timezone info will be fetched based on where user is logged in from
    # so we can fetch this info from user's browser
    # we may need to handle it differently if user is let's say travelling
    # because he will add the task in diff timezones.
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
