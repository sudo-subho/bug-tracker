from django.contrib import admin
from .models import UserProfile, Project, Bug, Notification

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Bug)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'user', 'notification_type', 'message', 'created_at', 'read')
    list_filter = ('notification_type', 'read')
    search_fields = ('user__username', 'sender__username', 'message')