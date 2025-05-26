from django.contrib import admin
from django import forms

from simple_history.admin import SimpleHistoryAdmin
from taggit.forms import TagWidget

from .models import Project, Task


# ---  custom ModelForm to render TaggableManager with TagWidget ---
class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'tags': TagWidget,  # familiar tag-entry UI
        }


# ---  Inline Task on Project pages ---
class TaskInline(admin.TabularInline):
    model = Task
    form = TaskAdminForm
    extra = 0
    fields = ('title', 'status', 'is_completed', 'order')
    readonly_fields = ('get_duration_display',)
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display    = ('title', 'user', 'created_at', 'task_count')
    list_filter     = ('user',)
    search_fields   = ('title', 'user__email')
    date_hierarchy  = 'created_at'
    inlines         = [TaskInline]

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Number of Tasks'


@admin.register(Task)
class TaskAdmin(SimpleHistoryAdmin):
    form                 = TaskAdminForm
    list_display         = (
        'title',
        'user',
        'status',
        'is_completed',
        'order',
        'project',
        'get_duration_display',
    )
    list_display_links   = ('title',)
    list_filter          = ('status', 'is_completed', 'project')
    search_fields        = ('title', 'description', 'user__email')
    date_hierarchy       = 'created_at'
    ordering             = ('-id',)
    autocomplete_fields  = ('user', 'project')  # now safe, UserAdmin has search_fields
    # DO NOT use filter_horizontal on tags—TaggableManager uses a custom through model
    # Instead rely on TagWidget via the ModelForm

    actions = ('mark_completed', 'mark_in_progress')

    history_list_display = ('status', 'is_completed', 'title')
    history_list_per_page = 50

    def mark_completed(self, request, queryset):
        updated = queryset.update(status=Task.COMPLETED, is_completed=True)
        self.message_user(request, f"{updated} task(s) marked completed.")
    mark_completed.short_description = 'Mark selected tasks as completed'

    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=Task.ON_BOARD, is_completed=False)
        self.message_user(request, f"{updated} task(s) marked in progress.")
    mark_in_progress.short_description = 'Mark selected tasks as in progress'

    def get_queryset(self, request):
        # join FK and prefetch tags to avoid N+1s
        return (
            super()
            .get_queryset(request)
            .select_related('user', 'project')
            .prefetch_related('tags')
        )
