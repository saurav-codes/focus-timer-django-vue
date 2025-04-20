from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.
from .models import User


class UserAdmin(SimpleHistoryAdmin):
    list_display = ('username', 'email', 'is_staff', 'joined_from_source')

admin.site.register(User, UserAdmin)