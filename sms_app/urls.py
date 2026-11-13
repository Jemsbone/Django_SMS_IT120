from django.urls import path
from .views import SendSMSView, SMSHistoryView

app_name = 'sms_app'

urlpatterns = [
    path('', SendSMSView.as_view(), name='send_sms'),
    path('history/', SMSHistoryView.as_view(), name='history'),
]

