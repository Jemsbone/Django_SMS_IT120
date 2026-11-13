from django.db import models


class SMSLog(models.Model):
    """
    Model representing the audit log for each SMS transmission attempt.
    Persisted in PostgreSQL as required by IT 120 course specifications.
    """
    STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
    ]

    recipient = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="Recipient Phone Number",
        help_text="Phone number in international (e.g. +639123456789) or local (09123456789) format"
    )
    message = models.TextField(
        verbose_name="Message Content",
        help_text="The SMS body text submitted to the gateway"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='SENT',
        db_index=True,
        verbose_name="Dispatch Status"
    )
    response_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Gateway Response Code",
        help_text="HTTP response code returned by the Textlink SMS API (e.g., 200, 400, 401)"
    )
    gateway_response = models.TextField(
        null=True,
        blank=True,
        verbose_name="Raw Gateway Response",
        help_text="Full response body or diagnostic error detail from Textlink"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Timestamp"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] To: {self.recipient} | Status: {self.status}"

    @property
    def is_success(self):
        return self.status == 'SENT'
