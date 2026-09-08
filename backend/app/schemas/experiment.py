from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.experiments.assignment import validate_assignment_contract
from app.experiments.metric_contract import resolve_metric

SrmMethod = Literal["exact_binomial", "pearson_chi_square", "not_tested"]
SrmReason = Literal["no_exposures", "insufficient_expected_count"]
EffectDirection = Literal["positive", "negative", "neutral"]
NumberNeededType = Literal["nnt", "nnh"]
DecisionCode = Literal[
    "investigate_srm",
    "do_not_ship_guardrail_regression",
    "collect_more_data",
    "ship_treatment",
    "stop_treatment",
    "inconclusive_collect_more_data",
]


class ExperimentCreate(BaseModel):
    key: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    name: str = Field(min_length=1, max_length=160)
    hypothesis: str = Field(min_length=1, max_length=500)
    primary_metric: str = Field(default="purchase_rate_14d", min_length=1, max_length=80)
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


class ExposureResponse(BaseModel):
    variant: str
    status: Literal["exposed"]


class ExperimentMetricResult(BaseModel):
    key: str
    label: str
    event_name: str
    window_days: int = Field(gt=0)


class VariantResult(BaseModel):
    variant: str
    n: int = Field(ge=0)
    conversions: int = Field(ge=0)
    conversion_rate: float = Field(ge=0, le=1)


class SrmResult(BaseModel):
    alpha: float = Field(gt=0, lt=1)
    total: int = Field(ge=0)
    observed: dict[str, int]
    expected: dict[str, float]
    method: SrmMethod
    tested: bool
    detected: bool
    chi_square: float = Field(ge=0)
    p_value: float = Field(ge=0, le=1)
    reason: SrmReason | None = None


class EffectSizeResult(BaseModel):
    risk_difference: float
    relative_lift: float | None
    risk_ratio: float | None
    odds_ratio: float | None
    number_needed: float | None
    number_needed_type: NumberNeededType | None
    direction: EffectDirection


class PowerResult(BaseModel):
    alpha: float = Field(gt=0, lt=1)
    target_power: float = Field(gt=0, lt=1)
    allocation_ratio: float = Field(gt=0)
    control_n: int = Field(gt=0)
    treatment_n: int = Field(gt=0)
    target_relative_lift: float = Field(gt=0)
    target_absolute_lift: float = Field(gt=0)
    power_at_target_effect: float = Field(ge=0, le=1)
    mde_absolute: float = Field(gt=0)
    mde_relative: float = Field(gt=0)
    required_control_n: int = Field(gt=0)
    required_treatment_n: int = Field(gt=0)
    adequately_powered_for_target: bool


class BinaryAnalysisResult(BaseModel):
    control_rate: float = Field(ge=0, le=1)
    treatment_rate: float = Field(ge=0, le=1)
    absolute_lift: float
    relative_lift: float | None
    standard_error: float = Field(ge=0)
    z_stat: float
    p_value: float = Field(ge=0, le=1)
    difference_ci: list[float] = Field(min_length=2, max_length=2)
    confidence_level: float = Field(gt=0, lt=1)
    alpha: float = Field(gt=0, lt=1)
    significant: bool
    effect_size: EffectSizeResult
    power: PowerResult | None


class ExperimentResults(BaseModel):
    experiment_id: UUID
    metric: ExperimentMetricResult
    variants: list[VariantResult]
    counts: dict[str, int]
    conversion_rates: dict[str, float]
    srm: SrmResult
    analysis: BinaryAnalysisResult | None
    decision: DecisionCode
