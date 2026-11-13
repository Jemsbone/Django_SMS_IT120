from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.views import View

from .forms import SMSForm
from .models import SMSLog
from .services import TextlinkSMSService


class SendSMSView(View):
    """
    Primary view for composing, validating, and dispatching SMS messages.
    Includes validation feedback, gateway response logging, and recent activity preview.
    """
    template_name = 'sms_app/send_sms.html'

    def get(self, request):
        initial_data = {}
        default_phone = getattr(settings, 'DEFAULT_RECIPIENT_PHONE', '').strip()
        if default_phone:
            initial_data['recipient'] = default_phone

        form = SMSForm(initial=initial_data)
        recent_logs = SMSLog.objects.all()[:5]
        total_count = SMSLog.objects.count()
        sent_count = SMSLog.objects.filter(status='SENT').count()

        context = {
            'form': form,
            'recent_logs': recent_logs,
            'total_count': total_count,
            'sent_count': sent_count,
            'page_title': 'Compose & Send SMS',
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SMSForm(request.POST)

        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            message_content = form.cleaned_data['message']

            # Dispatch via Textlink SMS Gateway service
            service = TextlinkSMSService()
            result = service.send_sms(recipient, message_content)

            status_val = 'SENT' if result['success'] else 'FAILED'

            # Persist audit record in PostgreSQL
            try:
                log_entry = SMSLog.objects.create(
                    recipient=recipient,
                    message=message_content,
                    status=status_val,
                    response_code=result.get('status_code'),
                    gateway_response=result.get('raw_response', '')
                )
            except Exception as db_err:
                log_entry = None
                messages.warning(
                    request,
                    f"Warning: SMS processed, but logging to database failed: {str(db_err)}"
                )

            # Display clear user feedback
            if result['success']:
                messages.success(
                    request,
                    f"Success! {result['message']}"
                )
                return redirect('sms_app:history')
            else:
                messages.error(
                    request,
                    f"Transmission Failed: {result['message']}"
                )
        else:
            messages.error(
                request,
                "Form submission error. Please check the entered phone number and message."
            )

        recent_logs = SMSLog.objects.all()[:5]
        context = {
            'form': form,
            'recent_logs': recent_logs,
            'total_count': SMSLog.objects.count(),
            'sent_count': SMSLog.objects.filter(status='SENT').count(),
            'page_title': 'Compose & Send SMS',
        }
        return render(request, self.template_name, context)


class SMSHistoryView(View):
    """
    Dashboard view for inspecting past SMS transmissions stored in PostgreSQL.
    Provides search, status filters, and pagination.
    """
    template_name = 'sms_app/history.html'

    def get(self, request):
        status_filter = request.GET.get('status', '').strip().upper()
        search_query = request.GET.get('q', '').strip()

        logs_qs = SMSLog.objects.all()

        # Filter by status
        if status_filter in ('SENT', 'FAILED'):
            logs_qs = logs_qs.filter(status=status_filter)

        # Filter by search term
        if search_query:
            logs_qs = logs_qs.filter(
                Q(recipient__icontains=search_query) |
                Q(message__icontains=search_query) |
                Q(gateway_response__icontains=search_query)
            )

        # Aggregate metrics
        stats = SMSLog.objects.aggregate(
            total=Count('id'),
            sent=Count('id', filter=Q(status='SENT')),
            failed=Count('id', filter=Q(status='FAILED'))
        )

        # Pagination: 10 logs per page
        paginator = Paginator(logs_qs, 10)
        page_number = request.GET.get('page', 1)

        try:
            page_obj = paginator.get_page(page_number)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.get_page(1)

        context = {
            'page_obj': page_obj,
            'stats': stats,
            'status_filter': status_filter,
            'search_query': search_query,
            'page_title': 'SMS Transmission History & Logs',
        }
        return render(request, self.template_name, context)
