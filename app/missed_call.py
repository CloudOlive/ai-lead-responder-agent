"""Core missed-call text-back logic, kept free of FastAPI/Twilio for easy testing."""

from app.business import Business
from app.messaging import MessageSender

# Dial outcomes that mean nobody picked up
MISSED_STATUSES = {"no-answer", "busy", "failed"}


def is_missed(dial_call_status: str) -> bool:
    return dial_call_status.strip().lower() in MISSED_STATUSES


def handle_call_status(
    dial_call_status: str, caller: str, business: Business, sender: MessageSender
) -> bool:
    """Text the caller back if the forwarded call was missed. Returns True if a text was sent."""
    if not is_missed(dial_call_status) or not caller:
        return False
    sender.send(to=caller, body=business.render_missed_call_message())
    return True
