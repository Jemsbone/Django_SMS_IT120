import re
from django import forms


class SMSForm(forms.Form):
    """
    Form for composing and validating outbound SMS messages.
    Includes custom validation for phone number formats and message length.
    """
    recipient = forms.CharField(
        label="Recipient Phone Number",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '+639123456789 or 09123456789',
            'id': 'id_recipient',
            'autocomplete': 'tel',
            'pattern': r'^\+?[0-9]{10,15}$',
            'title': 'Enter a valid phone number with optional + country code (10-15 digits)',
        }),
        help_text="Format: +639XXXXXXXXX (International) or 09XXXXXXXXX (Local PH)"
    )

    message = forms.CharField(
        label="Message Content",
        max_length=480,
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Type your SMS message here...',
            'id': 'id_message',
            'maxlength': '480',
        }),
        help_text="Standard SMS is 160 characters (1 credit). Max allowed: 480 characters (3 segments)."
    )

    def clean_recipient(self):
        """
        Sanitize and validate the recipient phone number.
        Strips whitespace, hyphens, and parentheses.
        """
        raw_number = self.cleaned_data.get('recipient', '').strip()
        
        # Remove hyphens, spaces, and parentheses
        sanitized = re.sub(r'[\s\-\(\)\.]', '', raw_number)

        if not sanitized:
            raise forms.ValidationError("Recipient phone number is required.")

        # Check for valid phone number pattern (+ followed by 10-15 digits or 10-15 digits)
        e164_pattern = r'^\+?[1-9]\d{9,14}$'
        local_ph_pattern = r'^09\d{9}$'

        if not (re.match(e164_pattern, sanitized) or re.match(local_ph_pattern, sanitized)):
            raise forms.ValidationError(
                "Invalid phone number format. Please provide a valid 11-digit mobile number "
                "(e.g., 09123456789) or international format (+639123456789)."
            )

        # Normalize local Philippine number starting with 09 to international E.164 format (+639...)
        if sanitized.startswith('09') and len(sanitized) == 11:
            sanitized = '+63' + sanitized[1:]

        return sanitized

    def clean_message(self):
        """
        Validate the message text body.
        Prevents empty strings and blank whitespace messages.
        """
        message_text = self.cleaned_data.get('message', '').strip()

        if not message_text:
            raise forms.ValidationError("SMS message body cannot be empty or contain only blank spaces.")

        if len(message_text) > 480:
            raise forms.ValidationError(
                f"Message length ({len(message_text)} characters) exceeds the maximum limit of 480 characters."
            )

        return message_text

