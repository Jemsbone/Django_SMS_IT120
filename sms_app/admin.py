from django.contrib import admin
from .models import SMSLog


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'short_message', 'status_badge', 'response_code', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('recipient', 'message', 'gateway_response')
    readonly_fields = ('recipient', 'message', 'status', 'response_code', 'gateway_response', 'timestamp')
    ordering = ('-timestamp',)

    def short_message(self, obj):
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    short_message.short_description = "Message"

    def status_badge(self, obj):
        return obj.status
    status_badge.short_description = "Status"

    def has_add_permission(self, request):
        # SMS logs are created via the application sending service, not manually added
        return False
