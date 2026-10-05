"""FastAPI app: Twilio voice webhooks for missed-call text-back."""

from functools import lru_cache

from fastapi import Depends, FastAPI, Form, Response
from twilio.twiml.voice_response import Dial, VoiceResponse

from app.business import Business, get_business
from app.config import get_settings
from app.messaging import FakeSender, MessageSender, TwilioSender
from app.missed_call import handle_call_status, is_missed
from app.security import verify_twilio_signature

DIAL_TIMEOUT_SECONDS = 20

app = FastAPI(title="AI Lead Responder")


@lru_cache
def get_sender() -> MessageSender:
    settings = get_settings()
    if settings.demo_mode:
        return FakeSender()
    return TwilioSender(
        settings.twilio_account_sid,
        settings.twilio_auth_token,
        settings.twilio_phone_number,
    )


def twiml(response: VoiceResponse) -> Response:
    return Response(content=str(response), media_type="application/xml")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/voice", dependencies=[Depends(verify_twilio_signature)])
def voice(business: Business = Depends(get_business)) -> Response:
    """Incoming call: ring the owner for 20s, then Twilio posts the result to /call-status."""
    response = VoiceResponse()
    dial = Dial(timeout=DIAL_TIMEOUT_SECONDS, action="/call-status", method="POST")
    dial.number(business.owner_phone)
    response.append(dial)
    return twiml(response)


@app.post("/call-status", dependencies=[Depends(verify_twilio_signature)])
def call_status(
    dial_call_status: str = Form("", alias="DialCallStatus"),
    caller: str = Form("", alias="From"),
    business: Business = Depends(get_business),
    sender: MessageSender = Depends(get_sender),
) -> Response:
    """Dial finished: if nobody answered, text the caller back."""
    handle_call_status(dial_call_status, caller, business, sender)
    response = VoiceResponse()
    if is_missed(dial_call_status):
        response.say(f"Sorry we missed your call. {business.name} will text you shortly.")
    response.hangup()
    return twiml(response)
