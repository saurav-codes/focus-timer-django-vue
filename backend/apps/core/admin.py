from django.contrib import admin
from .models import Task, Project
from simple_history.admin import SimpleHistoryAdmin



class TaskAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'user', 'order')
    # list_filter = ('status',)
    # search_fields = ('title',)
    # list_per_page = 10
    # list_editable = ('status',)

class ProjectAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'created_at', 'user')

admin.site.register(Task, TaskAdmin)
admin.site.register(Project, ProjectAdmin)