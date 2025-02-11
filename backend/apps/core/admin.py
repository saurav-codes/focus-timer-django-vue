from django.contrib import admin
from .models import Task



class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'order')
    list_filter = ('status',)
    search_fields = ('title',)
    list_editable = ('status',)
    list_per_page = 10


admin.site.register(Task, TaskAdmin)