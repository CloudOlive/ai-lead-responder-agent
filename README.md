# AI Lead Responder Agent

When a small business misses a call, instantly text the caller back. (Claude-powered
reply drafting, dashboard and demo mode arrive in later milestones; see CLAUDE.md.)

## Milestone 1: missed-call text-back

1. A customer calls your Twilio number. Twilio hits `POST /voice`.
2. `/voice` forwards the call to the owner's phone and rings for 20 seconds.
3. When the dial ends, Twilio posts the result to `POST /call-status`.
4. If `DialCallStatus` is `no-answer`, `busy` or `failed`, the caller gets a text
   built from `missed_call_message` in `business.yaml`.

### Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your Twilio values
pytest                        # all tests use FakeSender, no Twilio needed
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
ngrok http 8000
```

Put the `https://...ngrok-free.app` URL in `.env` as `PUBLIC_BASE_URL`, restart
uvicorn, then in the Twilio console set your number's **A call comes in** webhook to
`<PUBLIC_BASE_URL>/voice` (HTTP POST).

Set `DEMO_MODE=true` to run without Twilio: texts are printed by `FakeSender` and
signature checks are skipped.
