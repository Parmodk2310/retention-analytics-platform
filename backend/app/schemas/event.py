from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_EVENTS = {
    "page_view",
    "signup",
    "session_start",
    "search",
    "add_to_cart",
    "checkout",
    "purchase",
    "session_end",
}
MAX_PROPERTIES_BYTES = 16_384


class EventIn(BaseModel):
    event_id: UUID | None = None
    user_id: UUID | None = None
    anonymous_id: str | None = Field(default=None, max_length=64)
    session_id: str | None = Field(default=None, max_length=64)
    event_name: str
    event_time: datetime
    revenue: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    properties: dict = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, max_length=128)

    @field_validator("event_name")
    @classmethod
    def event_allowlist(cls, value: str) -> str:
        if value not in ALLOWED_EVENTS:
            raise ValueError("unsupported event_name")
        return value

    @model_validator(mode="after")
    def validate_event(self) -> EventIn:
        if self.event_time.tzinfo is None or self.event_time.utcoffset() is None:
            raise ValueError("event_time must be timezone-aware")

        now = datetime.now(UTC)
        event_time = self.event_time.astimezone(UTC)
        if event_time > now + timedelta(minutes=10):
            raise ValueError("event_time is too far in the future")
        if event_time < now - timedelta(days=730):
            raise ValueError("event_time is older than the accepted history window")
        if len(json.dumps(self.properties, default=str).encode("utf-8")) > MAX_PROPERTIES_BYTES:
            raise ValueError("properties payload is too large")
        if self.event_name == "purchase" and self.revenue <= 0:
            raise ValueError("purchase events require positive revenue")
        return self


class EventBatch(BaseModel):
    events: list[EventIn] = Field(min_length=1, max_length=500)


class IngestResponse(BaseModel):
    accepted: int
    duplicated: int
