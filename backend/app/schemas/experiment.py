from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ExperimentCreate(BaseModel):
    key: str = Field(pattern=r"^[a-z0-9_\-]+$", max_length=80)
    name: str = Field(max_length=160)
    hypothesis: str = Field(max_length=500)
    primary_metric: str = "activation_rate"
    variants: list[str] = Field(min_length=2, max_length=5)
    traffic_allocation: dict[str, float]

    @model_validator(mode="after")
    def allocations(self):
        if set(self.variants) != set(self.traffic_allocation):
            raise ValueError("allocation keys must match variants")
        if abs(sum(self.traffic_allocation.values()) - 1.0) > 1e-9:
            raise ValueError("traffic allocation must sum to 1")
        return self


class ExperimentResponse(BaseModel):
    id: UUID
    key: str
    name: str
    hypothesis: str
    primary_metric: str
    variants: list
    traffic_allocation: dict
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
