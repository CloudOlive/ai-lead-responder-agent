"""Twilio webhook signature validation."""

from fastapi import Depends, HTTPException, Request
from twilio.request_validator import RequestValidator

from app.config import Settings, get_settings


async def verify_twilio_signature(
    request: Request, settings: Settings = Depends(get_settings)
) -> None:
    if settings.demo_mode:
        return
    # Behind ngrok the server sees a localhost URL, so rebuild the public one Twilio signed.
    url = str(request.url)
    if settings.public_base_url:
        url = settings.public_base_url + request.url.path
        if request.url.query:
            url += "?" + request.url.query
    form = await request.form()
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(settings.twilio_auth_token)
    if not validator.validate(url, dict(form), signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
