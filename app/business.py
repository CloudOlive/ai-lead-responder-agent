"""Business profile loaded from business.yaml."""

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from app.config import get_settings


@dataclass(frozen=True)
class Business:
    name: str
    owner_phone: str
    missed_call_message: str
    booking_link: str = ""
    owner_name: str = ""
    timezone: str = ""
    hours: dict[str, str] = field(default_factory=dict)
    faqs: list[dict[str, str]] = field(default_factory=list)
    urgency_keywords: list[str] = field(default_factory=list)

    def render_missed_call_message(self) -> str:
        return self.missed_call_message.format(
            business_name=self.name, booking_link=self.booking_link
        )


def load_business(path: str | Path, owner_phone_override: str = "") -> Business:
    data = yaml.safe_load(Path(path).read_text())
    if owner_phone_override:
        data["owner_phone"] = owner_phone_override
    return Business(**data)


@lru_cache
def get_business() -> Business:
    settings = get_settings()
    return load_business(settings.business_config_path, settings.owner_phone)
