from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

EventName = Literal[
    "page_view",
    "signup",
    "session_start",
    "search",
    "add_to_cart",
    "checkout",
    "purchase",
    "session_end",
]

MAX_PROPERTIES_BYTES = 16_384
MAX_BATCH_SIZE = 500
MAX_FUTURE_SKEW = timedelta(minutes=10)
MAX_EVENT_AGE = timedelta(days=730)


class EventIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_id: UUID | None = None
    user_id: UUID | None = None
    anonymous_id: str | None = Field(default=None, min_length=1, max_length=64)
    session_id: str | None = Field(default=None, min_length=1, max_length=64)
    event_name: EventName
    event_time: datetime
    revenue: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    properties: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if self.user_id is None and self.anonymous_id is None:
            raise ValueError("user_id or anonymous_id is required")

        if self.event_id is None and self.idempotency_key is None:
            raise ValueError("event_id or idempotency_key is required")

        if self.event_time.tzinfo is None or self.event_time.utcoffset() is None:
            raise ValueError("event_time must be timezone-aware")

        event_time = self.event_time.astimezone(UTC)
        now = datetime.now(UTC)

        if event_time > now + MAX_FUTURE_SKEW:
            raise ValueError("event_time is too far in the future")
        if event_time < now - MAX_EVENT_AGE:
            raise ValueError("event_time is older than the accepted history window")

        if self.event_name == "purchase":
            if self.revenue <= 0:
                raise ValueError("purchase events require positive revenue")
        elif self.revenue != 0:
            raise ValueError("revenue is only allowed for purchase events")

        try:
            properties_size = len(
                json.dumps(
                    self.properties,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("properties must be JSON-serializable") from exc

        if properties_size > MAX_PROPERTIES_BYTES:
            raise ValueError("properties payload is too large")

        self.event_time = event_time
        return self


class EventBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[EventIn] = Field(min_length=1, max_length=MAX_BATCH_SIZE)


class IngestResponse(BaseModel):
    accepted: int = Field(ge=0)
    duplicated: int = Field(ge=0)


class EnqueueResponse(BaseModel):
    queued: int = Field(ge=0)
    duplicated_in_batch: int = Field(ge=0)
    stream: str
    first_stream_id: str | None = None
    last_stream_id: str | None = None
