import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TextlinkSMSService:
    """
    Service client for integrating with the Textlink SMS REST API (https://textlinksms.com/).
    
    Handles:
    - Authorization headers and request serialization
    - Network timeout and exception handling
    - Gateway response status code classification
    - Development/Testing sandbox mode
    """

    def __init__(self):
        self.api_key = getattr(settings, 'TEXTLINK_API_KEY', '').strip()
        self.api_url = getattr(settings, 'TEXTLINK_API_URL', 'https://textlinksms.com/api/send').strip()
        self.sender_id = getattr(settings, 'TEXTLINK_SENDER_ID', 'IT120SMS').strip()
        self.timeout = 10  # 10 seconds connection/read timeout

    def send_sms(self, phone_number: str, message: str) -> dict:
        """
        Submits an SMS message to the Textlink SMS Gateway.

        :param phone_number: Validated recipient phone number (e.g., +639123456789 or 09123456789)
        :param message: Validated message body text
        :return: Standardized result dict with keys:
                 - success: bool
                 - status_code: int or None
                 - message: str (friendly explanation)
                 - raw_response: str (diagnostic auditing)
                 - message_id: str or None
        """
        # 1. Validation check for credentials
        if not self.api_key or self.api_key in ('', 'your_textlink_api_key_here'):
            return {
                'success': False,
                'status_code': 401,
                'message': (
                    "SMS Gateway Error: Missing or unconfigured TEXTLINK_API_KEY. "
                    "Please set your valid Textlink API Key in your .env configuration file."
                ),
                'raw_response': "ERR_MISSING_API_KEY: TEXTLINK_API_KEY is empty or using placeholder.",
                'message_id': None
            }

        # 2. Simulator/Demo mode for offline classroom tests or mock keys
        if self.api_key.lower().startswith('demo_') or self.api_key == 'test_api_key_placeholder':
            return {
                'success': True,
                'status_code': 200,
                'message': (
                    f"SMS successfully simulated! [DEMO MODE ACTIVE] "
                    f"Message queued for delivery to {phone_number}."
                ),
                'raw_response': json.dumps({
                    'status': 'success',
                    'mode': 'simulator',
                    'phone_number': phone_number,
                    'sender_id': self.sender_id,
                    'info': 'Sandbox simulation successful. Replace TEXTLINK_API_KEY with live key for real cellular broadcast.'
                }),
                'message_id': f"DEMO-{hash(phone_number + message) % 1000000:06d}"
            }

        # 3. Live Request Preparation
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        # Standard Textlink REST payload
        payload = {
            'phone_number': phone_number,
            'to': phone_number,
            'message': message,
            'text': message,
            'sender_id': self.sender_id,
            'api_key': self.api_key
        }

        # 4. Dispatch Request to Gateway
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            status_code = response.status_code
            raw_text = response.text

            try:
                data = response.json()
            except ValueError:
                data = {}

            # Evaluate Response
            if status_code in (200, 201):
                # Check for provider-level failure indicators inside JSON payload if any
                if isinstance(data, dict) and data.get('status') in ('error', 'failed', False):
                    err_msg = data.get('message') or data.get('error') or "Provider rejected the request."
                    return {
                        'success': False,
                        'status_code': status_code,
                        'message': f"Textlink Gateway returned an error: {err_msg}",
                        'raw_response': raw_text,
                        'message_id': data.get('message_id') or data.get('id')
                    }

                msg_id = None
                if isinstance(data, dict):
                    msg_id = data.get('message_id') or data.get('id') or data.get('reference')

                return {
                    'success': True,
                    'status_code': status_code,
                    'message': f"Message successfully transmitted to gateway for {phone_number}.",
                    'raw_response': raw_text,
                    'message_id': msg_id
                }

            elif status_code == 400:
                err_msg = data.get('message') if isinstance(data, dict) else raw_text
                return {
                    'success': False,
                    'status_code': 400,
                    'message': f"Gateway Bad Request (400): {err_msg or 'Invalid parameters or phone number format.'}",
                    'raw_response': raw_text,
                    'message_id': None
                }

            elif status_code in (401, 403):
                return {
                    'success': False,
                    'status_code': status_code,
                    'message': "Authentication Failed (401/403): Invalid or expired Textlink API Key.",
                    'raw_response': raw_text,
                    'message_id': None
                }

            elif status_code == 402:
                return {
                    'success': False,
                    'status_code': 402,
                    'message': "Payment Required (402): Insufficient Textlink account balance/SMS credits.",
                    'raw_response': raw_text,
                    'message_id': None
                }

            else:
                return {
                    'success': False,
                    'status_code': status_code,
                    'message': f"Textlink Gateway Server Error (HTTP {status_code}). Please retry shortly.",
                    'raw_response': raw_text,
                    'message_id': None
                }

        except requests.exceptions.Timeout:
            logger.error("Textlink API request timed out after %s seconds.", self.timeout)
            return {
                'success': False,
                'status_code': 504,
                'message': f"Gateway Connection Timeout: The request exceeded {self.timeout}s without response.",
                'raw_response': f"TIMEOUT_ERROR: Exceeded {self.timeout}s waiting for {self.api_url}",
                'message_id': None
            }

        except requests.exceptions.ConnectionError as ce:
            logger.error("Textlink API Connection Error: %s", ce)
            return {
                'success': False,
                'status_code': 503,
                'message': "Network / Connection Error: Unable to resolve or establish connection to Textlink gateway.",
                'raw_response': f"CONNECTION_ERROR: {str(ce)}",
                'message_id': None
            }

        except requests.exceptions.RequestException as re:
            logger.error("Unexpected Textlink API Request Exception: %s", re)
            return {
                'success': False,
                'status_code': 500,
                'message': f"Internal Communication Error: {str(re)}",
                'raw_response': f"REQUEST_EXCEPTION: {str(re)}",
                'message_id': None
            }

