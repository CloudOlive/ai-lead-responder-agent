"""Settings loaded from environment variables (and .env)."""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    demo_mode: bool
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    public_base_url: str
    owner_phone: str
    business_config_path: str


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        demo_mode=_env_bool("DEMO_MODE"),
        twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
        twilio_phone_number=os.getenv("TWILIO_PHONE_NUMBER", ""),
        public_base_url=os.getenv("PUBLIC_BASE_URL", "").rstrip("/"),
        owner_phone=os.getenv("OWNER_PHONE", "").strip(),
        business_config_path=os.getenv("BUSINESS_CONFIG_PATH", "business.yaml"),
    )
