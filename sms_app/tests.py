from unittest.mock import patch, Mock
import requests
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from .models import SMSLog
from .forms import SMSForm
from .services import TextlinkSMSService


class SMSFormTests(TestCase):
    """
    Test suite for SMSForm validation logic.
    """
    def test_valid_form_philippine_local(self):
        form = SMSForm(data={
            'recipient': '09123456789',
            'message': 'Hello from Django SMS Gateway!'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['recipient'], '+639123456789')
        self.assertEqual(form.cleaned_data['message'], 'Hello from Django SMS Gateway!')

    def test_valid_form_international_e164(self):
        form = SMSForm(data={
            'recipient': '+639123456789',
            'message': 'Valid international number test.'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['recipient'], '+639123456789')

    def test_phone_sanitization_removes_spaces_and_dashes(self):
        form = SMSForm(data={
            'recipient': '0912-345-6789',
            'message': 'Testing dash removal.'
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['recipient'], '+639123456789')

    def test_invalid_phone_number_alphabetic(self):
        form = SMSForm(data={
            'recipient': 'NOT_A_NUMBER',
            'message': 'Testing invalid phone.'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('recipient', form.errors)

    def test_invalid_phone_number_too_short(self):
        form = SMSForm(data={
            'recipient': '12345',
            'message': 'Testing short phone.'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('recipient', form.errors)

    def test_empty_message_validation(self):
        form = SMSForm(data={
            'recipient': '09123456789',
            'message': '   '
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_message_exceeding_max_length(self):
        form = SMSForm(data={
            'recipient': '09123456789',
            'message': 'A' * 481
        })
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)


class TextlinkSMSServiceTests(TestCase):
    """
    Test suite for TextlinkSMSService integration and error classification.
    """
    def setUp(self):
        self.service = TextlinkSMSService()

    def test_missing_api_key_handling(self):
        self.service.api_key = ''
        result = self.service.send_sms('+639123456789', 'Test Message')
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 401)
        self.assertIn('Missing or unconfigured TEXTLINK_API_KEY', result['message'])

    def test_demo_mode_simulation(self):
        self.service.api_key = 'test_api_key_placeholder'
        result = self.service.send_sms('+639123456789', 'Demo Simulation')
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 200)
        self.assertIn('DEMO MODE ACTIVE', result['message'])

    @patch('requests.post')
    def test_live_successful_gateway_response(self, mock_post):
        self.service.api_key = 'live_textlink_api_key_123'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success", "message_id": "TL-999"}'
        mock_response.json.return_value = {"status": "success", "message_id": "TL-999"}
        mock_post.return_value = mock_response

        result = self.service.send_sms('+639123456789', 'Hello Live API')
        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['message_id'], 'TL-999')

    @patch('requests.post')
    def test_gateway_authentication_error(self, mock_post):
        self.service.api_key = 'live_textlink_api_key_123'
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = '{"error": "Unauthorized"}'
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_post.return_value = mock_response

        result = self.service.send_sms('+639123456789', 'Hello Auth Fail')
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 401)
        self.assertIn('Authentication Failed', result['message'])

    @patch('requests.post')
    def test_gateway_insufficient_credits_error(self, mock_post):
        self.service.api_key = 'live_textlink_api_key_123'
        mock_response = Mock()
        mock_response.status_code = 402
        mock_response.text = '{"error": "Insufficient Credits"}'
        mock_response.json.return_value = {"error": "Insufficient Credits"}
        mock_post.return_value = mock_response

        result = self.service.send_sms('+639123456789', 'Hello No Credits')
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 402)
        self.assertIn('Payment Required', result['message'])

    @patch('requests.post')
    def test_gateway_timeout_exception(self, mock_post):
        self.service.api_key = 'live_textlink_api_key_123'
        mock_post.side_effect = requests.exceptions.Timeout("Connection timed out")

        result = self.service.send_sms('+639123456789', 'Hello Timeout')
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 504)
        self.assertIn('Gateway Connection Timeout', result['message'])

    @patch('requests.post')
    def test_gateway_connection_error(self, mock_post):
        self.service.api_key = 'live_textlink_api_key_123'
        mock_post.side_effect = requests.exceptions.ConnectionError("Failed to resolve host")

        result = self.service.send_sms('+639123456789', 'Hello DNS Fail')
        self.assertFalse(result['success'])
        self.assertEqual(result['status_code'], 503)
        self.assertIn('Network / Connection Error', result['message'])


class SMSLogModelTests(TestCase):
    """
    Test suite for SMSLog model persistence and methods.
    """
    def test_model_creation_and_properties(self):
        log = SMSLog.objects.create(
            recipient='+639123456789',
            message='Unit testing SMSLog model.',
            status='SENT',
            response_code=200,
            gateway_response='{"status": "ok"}'
        )
        self.assertEqual(log.recipient, '+639123456789')
        self.assertTrue(log.is_success)
        self.assertIn('+639123456789', str(log))
        self.assertIn('SENT', str(log))


class SMSViewsTests(TestCase):
    """
    Test suite for Django views and template rendering.
    """
    def setUp(self):
        self.client = Client()

    def test_send_sms_view_get(self):
        response = self.client.get(reverse('sms_app:send_sms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compose SMS Message')
        self.assertContains(response, 'Textlink Gateway')

    def test_send_sms_view_post_success(self):
        response = self.client.post(reverse('sms_app:send_sms'), {
            'recipient': '09123456789',
            'message': 'Automated view test message.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        # Verify log created
        log = SMSLog.objects.filter(recipient='+639123456789').first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'SENT')

    def test_send_sms_view_post_invalid_phone(self):
        response = self.client.post(reverse('sms_app:send_sms'), {
            'recipient': 'invalid_num',
            'message': 'Testing invalid form submission.'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid phone number format')

    def test_sms_history_view_get(self):
        # Create test records
        SMSLog.objects.create(recipient='+639111111111', message='Message 1', status='SENT', response_code=200)
        SMSLog.objects.create(recipient='+639222222222', message='Message 2', status='FAILED', response_code=400)

        response = self.client.get(reverse('sms_app:history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '+639111111111')
        self.assertContains(response, '+639222222222')
        self.assertContains(response, 'SMS Audit Logs')

    def test_sms_history_view_filter_status(self):
        SMSLog.objects.create(recipient='+639111111111', message='Message 1', status='SENT', response_code=200)
        SMSLog.objects.create(recipient='+639222222222', message='Message 2', status='FAILED', response_code=400)

        response = self.client.get(reverse('sms_app:history') + '?status=FAILED')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '+639222222222')
        self.assertNotContains(response, '+639111111111')
