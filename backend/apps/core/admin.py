from django.contrib import admin
from .models import Task



class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    # list_filter = ('status',)
    # search_fields = ('title',)
    # list_per_page = 10
    # list_editable = ('status',)


admin.site.register(Task, TaskAdmin)
