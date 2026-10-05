"""SMS sending. Everything that sends a text goes through MessageSender."""

from dataclasses import dataclass
from typing import Protocol

from twilio.rest import Client


class MessageSender(Protocol):
    def send(self, to: str, body: str) -> str:
        """Send an SMS and return a message id."""
        ...


class TwilioSender:
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        self._client = Client(account_sid, auth_token)
        self._from = from_number

    def send(self, to: str, body: str) -> str:
        message = self._client.messages.create(to=to, from_=self._from, body=body)
        return message.sid


@dataclass
class SentMessage:
    to: str
    body: str


class FakeSender:
    """Records messages instead of sending them. Used in DEMO_MODE and tests."""

    def __init__(self) -> None:
        self.sent: list[SentMessage] = []

    def send(self, to: str, body: str) -> str:
        self.sent.append(SentMessage(to=to, body=body))
        print(f"[FakeSender] to={to}: {body}")
        return f"FAKE{len(self.sent):06d}"
