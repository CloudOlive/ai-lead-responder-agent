# AI Lead Responder Agent

## Purpose
Portfolio project and service prototype: when a small business misses a call,
instantly text the caller back, then use Claude to classify and draft replies to
their texts. Also handles web form inquiries. Dashboard shows leads and response times.

## Stack
- Python 3.11+, FastAPI, Uvicorn
- Twilio (voice + SMS webhooks)
- Anthropic Claude API (classification + reply drafting)
- SQLite via SQLModel
- Simple server-rendered HTML dashboard (Jinja2), no frontend framework

## Architecture rules
- All business-specific details (name, hours, FAQs, booking link, owner phone,
  urgency keywords) live in business.yaml, never hardcoded.
- SMS sending goes through a MessageSender interface with two implementations:
  TwilioSender and FakeSender. DEMO_MODE=true uses FakeSender so the project runs
  with no Twilio account.
- Secrets only via .env; maintain .env.example with placeholder values.
- Validate Twilio request signatures on webhooks (skip in DEMO_MODE).
- Handle STOP/opt-out replies.
- Messages that mention money, complaints, or urgency are flagged for owner
  approval rather than auto-sent.

## Milestones
1. Missed-call text-back working on a real phone via ngrok
2. Inbound SMS webhook + Claude classify/draft
3. SQLite logging + dashboard with response-time metrics
4. Demo mode with browser-based fake phone + web form intake
5. README, demo GIF, deployment

## Conventions
- Small, readable modules; type hints; pytest tests for core logic
- Keep it simple: this is a demo a hiring manager or business owner should
  understand in 5 minutes.
