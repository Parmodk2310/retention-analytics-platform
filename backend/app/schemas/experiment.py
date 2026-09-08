from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.experiments.assignment import validate_assignment_contract
from app.experiments.metric_contract import resolve_metric


class ExperimentCreate(BaseModel):
    key: str = Field(
        min_length=1,
        max_length=80,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )
    name: str = Field(min_length=1, max_length=160)
    hypothesis: str = Field(min_length=1, max_length=500)
    primary_metric: str = Field(
        default="purchase_rate_14d",
        min_length=1,
        max_length=80,
    )
    variants: list[str] = Field(min_length=2, max_length=5)
    traffic_allocation: dict[str, float]
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        validate_assignment_contract(self.variants, self.traffic_allocation)
        resolve_metric(self.primary_metric)

        if self.starts_at and self.ends_at and self.starts_at >= self.ends_at:
            raise ValueError("starts_at must be before ends_at")

        return self


class ExperimentResponse(BaseModel):
    id: UUID
    key: str
    name: str
    hypothesis: str
    primary_metric: str
    variants: list[str]
    traffic_allocation: dict[str, float]
    status: str
    starts_at: datetime | None
    ends_at: datetime | None

    model_config = {"from_attributes": True}


class AssignmentResponse(BaseModel):
    experiment_id: UUID
    user_id: UUID
    variant: str


class ExperimentResults(BaseModel):
    experiment_id: UUID
    counts: dict[str, int]
    conversion_rates: dict[str, float]
    srm: dict
    analysis: dict | None
    decision: str
