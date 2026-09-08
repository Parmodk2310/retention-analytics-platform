from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Experiment, ExperimentAssignment, ExperimentExposure
from app.experiments.assignment import assign_variant, validate_assignment_contract
from app.experiments.decision import recommend
from app.experiments.metrics import binary_conversion_counts
from app.experiments.srm import sample_ratio_mismatch
from app.experiments.stats import analyze_binary
from app.schemas.experiment import ExperimentCreate

DEFAULT_CONVERSION_EVENT = "purchase"
DEFAULT_WINDOW_DAYS = 14


def _assignment_query(experiment_id: UUID, user_id: UUID):
    return select(ExperimentAssignment).where(
        ExperimentAssignment.experiment_id == experiment_id,
        ExperimentAssignment.user_id == user_id,
    )


def _variants(experiment: Experiment) -> list[str]:
    variants = [str(value) for value in experiment.variants]
    validate_assignment_contract(variants, experiment.traffic_allocation)
    return variants


async def create_experiment(
    db: AsyncSession,
    payload: ExperimentCreate,
) -> Experiment:
    experiment = Experiment(**payload.model_dump())
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    return experiment


async def list_experiments(db: AsyncSession) -> list[Experiment]:
    rows = await db.scalars(select(Experiment).order_by(Experiment.created_at.desc()))
    return list(rows.all())


async def get_or_assign(
    db: AsyncSession,
    experiment: Experiment,
    user_id: UUID,
) -> ExperimentAssignment:
    variants = _variants(experiment)
    query = _assignment_query(experiment.id, user_id)

    if existing := await db.scalar(query):
        if existing.variant not in variants:
            raise RuntimeError("persisted assignment has an unknown variant")
        return existing

    variant = assign_variant(
        str(user_id),
        str(experiment.id),
        experiment.traffic_allocation,
        variants=variants,
    )

    statement = (
        insert(ExperimentAssignment)
        .values(
            experiment_id=experiment.id,
            user_id=user_id,
            variant=variant,
        )
        .on_conflict_do_nothing(constraint="uq_assignment_experiment_user")
    )

    await db.execute(statement)
    await db.commit()

    assignment = await db.scalar(query)
    if assignment is None:
        raise RuntimeError("failed to create experiment assignment")

    return assignment


async def expose(
    db: AsyncSession,
    experiment: Experiment,
    user_id: UUID,
) -> str:
    assignment = await get_or_assign(db, experiment, user_id)

    statement = (
        insert(ExperimentExposure)
        .values(
            experiment_id=experiment.id,
            user_id=user_id,
            variant=assignment.variant,
            exposed_at=datetime.now(UTC),
        )
        .on_conflict_do_nothing(constraint="uq_exposure_experiment_user")
    )

    await db.execute(statement)
    await db.commit()
    return assignment.variant


async def results(
    db: AsyncSession,
    experiment: Experiment,
) -> dict:
    variants = _variants(experiment)

    counts = await binary_conversion_counts(
        db,
        str(experiment.id),
        DEFAULT_CONVERSION_EVENT,
        DEFAULT_WINDOW_DAYS,
    )

    observed = {variant: counts.get(variant, {}).get("n", 0) for variant in variants}
    rates = {
        variant: (
            counts.get(variant, {}).get("conversions", 0) / observed[variant]
            if observed[variant]
            else 0.0
        )
        for variant in variants
    }

    srm = sample_ratio_mismatch(observed, experiment.traffic_allocation)
    analysis = None

    if len(variants) == 2 and all(observed[v] > 0 for v in variants):
        control, treatment = variants

        analysis = analyze_binary(
            counts[control]["conversions"],
            counts[control]["n"],
            counts[treatment]["conversions"],
            counts[treatment]["n"],
        )

    return {
        "experiment_id": experiment.id,
        "counts": observed,
        "conversion_rates": rates,
        "srm": srm,
        "analysis": analysis,
        "decision": recommend(srm, analysis),
    }
