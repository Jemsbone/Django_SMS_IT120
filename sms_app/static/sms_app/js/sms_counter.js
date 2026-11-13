/**
 * Real-Time Character Counter, Segment Calculator & Live Smartphone Preview
 * IT 120 - Django Textlink SMS Application
 */

document.addEventListener('DOMContentLoaded', function () {
    const messageInput = document.getElementById('id_message');
    const recipientInput = document.getElementById('id_recipient');
    const charCountEl = document.getElementById('charCount');
    const segmentInfoEl = document.getElementById('segmentInfo');
    const charCounterBadge = document.getElementById('charCounterBadge');
    
    // Live Preview elements
    const previewRecipient = document.getElementById('previewRecipient');
    const previewText = document.getElementById('previewText');
    const previewTimestamp = document.getElementById('previewTimestamp');

    // Action buttons & form
    const smsForm = document.getElementById('smsForm');
    const sendBtn = document.getElementById('sendBtn');
    const btnIcon = document.getElementById('btnIcon');
    const btnText = document.getElementById('btnText');
    const clearBtn = document.getElementById('clearBtn');

    const STANDARD_SMS_LENGTH = 160;
    const MAX_ALLOWED_LENGTH = 480;

    function updateCharacterCountAndPreview() {
        if (!messageInput) return;

        const currentText = messageInput.value;
        const length = currentText.length;

        // Update counter number
        if (charCountEl) {
            charCountEl.textContent = length;
        }

        // Calculate segment / credit consumption
        let segments = 1;
        if (length > 320) {
            segments = 3;
        } else if (length > 160) {
            segments = 2;
        } else if (length === 0) {
            segments = 1;
        }

        if (segmentInfoEl) {
            segmentInfoEl.textContent = `${segments} SMS credit${segments > 1 ? 's' : ''}`;
        }

        // Badge styling based on length
        if (charCounterBadge) {
            if (length > STANDARD_SMS_LENGTH) {
                charCounterBadge.className = 'badge bg-warning-subtle text-warning-emphasis border border-warning-subtle';
            } else {
                charCounterBadge.className = 'badge bg-secondary-subtle text-secondary border';
            }
        }

        // Synchronize Phone Mockup Message Bubble
        if (previewText) {
            if (currentText.trim() === '') {
                previewText.textContent = 'Your composed message will appear here in real-time...';
                previewText.classList.add('opacity-75', 'fst-italic');
            } else {
                previewText.textContent = currentText;
                previewText.classList.remove('opacity-75', 'fst-italic');
            }
        }

        if (previewTimestamp) {
            const now = new Date();
            previewTimestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }

    function updateRecipientPreview() {
        if (!recipientInput || !previewRecipient) return;

        const val = recipientInput.value.trim();
        if (val === '') {
            previewRecipient.textContent = '+63 9XX XXX XXXX';
        } else {
            previewRecipient.textContent = val;
        }
    }

    // Attach real-time listeners
    if (messageInput) {
        messageInput.addEventListener('input', updateCharacterCountAndPreview);
        messageInput.addEventListener('keyup', updateCharacterCountAndPreview);
        // Initial run in case form reloaded with data
        updateCharacterCountAndPreview();
    }

    if (recipientInput) {
        recipientInput.addEventListener('input', updateRecipientPreview);
        recipientInput.addEventListener('keyup', updateRecipientPreview);
        updateRecipientPreview();
    }

    // Clear form button handler
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            if (smsForm) {
                smsForm.reset();
                updateCharacterCountAndPreview();
                updateRecipientPreview();
                if (recipientInput) recipientInput.focus();
            }
        });
    }

    // Submit button UX feedback (spinner)
    if (smsForm && sendBtn) {
        smsForm.addEventListener('submit', function () {
            if (smsForm.checkValidity()) {
                sendBtn.disabled = true;
                if (btnIcon) {
                    btnIcon.className = 'spinner-border spinner-border-sm me-2';
                }
                if (btnText) {
                    btnText.textContent = 'Transmitting to Gateway...';
                }
                // Allow form submit to continue
                return true;
            }
        });
    }
});

