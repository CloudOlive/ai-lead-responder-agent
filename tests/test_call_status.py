import pytest
from fastapi.testclient import TestClient

from app.business import Business, get_business
from app.config import Settings, get_settings
from app.main import app, get_sender
from app.messaging import FakeSender
from app.missed_call import handle_call_status

BUSINESS = Business(
    name="Olive Consults LLC.",
    owner_phone="+15555550100",
    booking_link="https://example.com/book",
    missed_call_message="Hi, this is {business_name}. Book here: {booking_link}",
)
CALLER = "+15555550199"


@pytest.mark.parametrize("status", ["no-answer", "busy", "failed"])
def test_missed_statuses_text_the_caller(status: str) -> None:
    sender = FakeSender()
    assert handle_call_status(status, CALLER, BUSINESS, sender) is True
    assert len(sender.sent) == 1
    assert sender.sent[0].to == CALLER
    assert sender.sent[0].body == (
        "Hi, this is Olive Consults LLC.. Book here: https://example.com/book"
    )


@pytest.mark.parametrize("status", ["completed", "answered", "canceled", ""])
def test_answered_or_other_statuses_send_nothing(status: str) -> None:
    sender = FakeSender()
    assert handle_call_status(status, CALLER, BUSINESS, sender) is False
    assert sender.sent == []


def test_no_caller_number_sends_nothing() -> None:
    sender = FakeSender()
    assert handle_call_status("no-answer", "", BUSINESS, sender) is False
    assert sender.sent == []


@pytest.fixture
def client_and_sender():
    sender = FakeSender()
    app.dependency_overrides[get_sender] = lambda: sender
    app.dependency_overrides[get_business] = lambda: BUSINESS
    app.dependency_overrides[get_settings] = lambda: Settings(
        demo_mode=True,
        twilio_account_sid="",
        twilio_auth_token="",
        twilio_phone_number="",
        public_base_url="",
        owner_phone="",
        business_config_path="",
    )
    yield TestClient(app), sender
    app.dependency_overrides.clear()


def test_call_status_endpoint_texts_back_on_no_answer(client_and_sender) -> None:
    client, sender = client_and_sender
    resp = client.post("/call-status", data={"DialCallStatus": "no-answer", "From": CALLER})
    assert resp.status_code == 200
    assert "<Hangup" in resp.text
    assert [m.to for m in sender.sent] == [CALLER]


def test_call_status_endpoint_silent_when_answered(client_and_sender) -> None:
    client, sender = client_and_sender
    resp = client.post("/call-status", data={"DialCallStatus": "completed", "From": CALLER})
    assert resp.status_code == 200
    assert sender.sent == []


def test_voice_forwards_to_owner_with_20s_timeout(client_and_sender) -> None:
    client, _ = client_and_sender
    resp = client.post("/voice", data={"From": CALLER})
    assert resp.status_code == 200
    assert 'timeout="20"' in resp.text
    assert 'action="/call-status"' in resp.text
    assert "+15555550100</Number>" in resp.text


def test_signature_checked_outside_demo_mode() -> None:
    from twilio.request_validator import RequestValidator

    token = "test-token"
    base = "https://example.ngrok-free.app"
    sender = FakeSender()
    app.dependency_overrides[get_sender] = lambda: sender
    app.dependency_overrides[get_business] = lambda: BUSINESS
    app.dependency_overrides[get_settings] = lambda: Settings(
        demo_mode=False,
        twilio_account_sid="",
        twilio_auth_token=token,
        twilio_phone_number="",
        public_base_url=base,
        owner_phone="",
        business_config_path="",
    )
    try:
        client = TestClient(app)
        params = {"DialCallStatus": "busy", "From": CALLER}
        bad = client.post("/call-status", data=params, headers={"X-Twilio-Signature": "nope"})
        assert bad.status_code == 403
        assert sender.sent == []

        good_sig = RequestValidator(token).compute_signature(base + "/call-status", params)
        good = client.post("/call-status", data=params, headers={"X-Twilio-Signature": good_sig})
        assert good.status_code == 200
        assert len(sender.sent) == 1
    finally:
        app.dependency_overrides.clear()
