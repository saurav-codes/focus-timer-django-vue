from django.contrib import admin
from .models import Task, Project



class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    # list_filter = ('status',)
    # search_fields = ('title',)
    # list_per_page = 10
    # list_editable = ('status',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

admin.site.register(Task, TaskAdmin)
admin.site.register(Project, ProjectAdmin)