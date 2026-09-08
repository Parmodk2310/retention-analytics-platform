from datetime import date
from uuid import UUID

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChurnScore, ModelRun, User


VALID_RISK_BANDS = {
    "low",
    "medium",
    "high",
    "critical",
}

VALID_ACQUISITION_CHANNELS = {
    "organic",
    "email",
    "paid_social",
    "referral",
    "affiliate",
}

VALID_DEVICE_TYPES = {
    "web",
    "ios",
    "android",
}


def _normalize_dimension(value: str | None) -> str | None:
    """Normalize user-facing dimension values to stored canonical values."""

    if value is None:
        return None

    normalized = "_".join(value.strip().lower().replace("-", " ").split())

    return normalized or None


def _normalize_risk_band(value: str | None) -> str | None:
    """Normalize a risk-band filter."""

    if value is None:
        return None

    normalized = value.strip().lower()
    return normalized or None


def _validate_filters(
    risk_band: str | None,
    acquisition_channel: str | None,
    device_type: str | None,
) -> None:
    """Validate normalized churn filters."""

    if risk_band is not None and risk_band not in VALID_RISK_BANDS:
        raise ValueError("Invalid risk band.")

    if acquisition_channel is not None and acquisition_channel not in VALID_ACQUISITION_CHANNELS:
        raise ValueError("Invalid acquisition channel.")

    if device_type is not None and device_type not in VALID_DEVICE_TYPES:
        raise ValueError("Invalid device type.")


def _score_payload(
    score: ChurnScore,
    external_id: str,
    acquisition_channel: str,
    device_type: str,
) -> dict:
    """Serialize a persisted churn score."""

    return {
        "user_id": str(score.user_id),
        "external_id": external_id,
        "snapshot_date": score.snapshot_date,
        "score": float(score.score),
        "risk_band": score.risk_band,
        "model_version": score.model_version,
        "reasons": score.reasons or [],
        "scored_at": score.scored_at,
        "acquisition_channel": acquisition_channel,
        "device_type": device_type,
    }


async def latest_snapshot_date(db: AsyncSession) -> date | None:
    """Return the newest persisted scoring snapshot."""

    return await db.scalar(select(func.max(ChurnScore.snapshot_date)))


async def _latest_score_context(
    db: AsyncSession,
) -> tuple[date, str] | None:
    """
    Return the newest scoring snapshot and model version.

    Filtering by both fields prevents scores from different model versions
    on the same snapshot from being mixed in one API response.
    """

    row = (
        await db.execute(
            select(
                ChurnScore.snapshot_date,
                ChurnScore.model_version,
            )
            .order_by(
                desc(ChurnScore.snapshot_date),
                desc(ChurnScore.scored_at),
            )
            .limit(1)
        )
    ).first()

    if row is None:
        return None

    snapshot_date, model_version = row
    return snapshot_date, model_version


async def latest_scores(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    risk_band: str | None = None,
    acquisition_channel: str | None = None,
    device_type: str | None = None,
) -> list[dict]:
    """
    Return scores from the newest production snapshot and model version.

    Results are ordered from highest to lowest calibrated churn probability.
    """

    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")

    if offset < 0:
        raise ValueError("offset must be non-negative")

    risk_band = _normalize_risk_band(risk_band)
    acquisition_channel = _normalize_dimension(acquisition_channel)
    device_type = _normalize_dimension(device_type)

    _validate_filters(
        risk_band,
        acquisition_channel,
        device_type,
    )

    context = await _latest_score_context(db)

    if context is None:
        return []

    snapshot_date, model_version = context

    statement = (
        select(
            ChurnScore,
            User.external_id,
            User.acquisition_channel,
            User.device_type,
        )
        .join(
            User,
            User.id == ChurnScore.user_id,
        )
        .where(
            ChurnScore.snapshot_date == snapshot_date,
            ChurnScore.model_version == model_version,
        )
    )

    if risk_band is not None:
        statement = statement.where(ChurnScore.risk_band == risk_band)

    if acquisition_channel is not None:
        statement = statement.where(User.acquisition_channel == acquisition_channel)

    if device_type is not None:
        statement = statement.where(User.device_type == device_type)

    statement = (
        statement.order_by(
            desc(ChurnScore.score),
            User.external_id.asc(),
        )
        .offset(offset)
        .limit(limit)
    )

    rows = (await db.execute(statement)).all()

    return [
        _score_payload(
            score,
            external_id,
            acquisition_channel_value,
            device_type_value,
        )
        for (
            score,
            external_id,
            acquisition_channel_value,
            device_type_value,
        ) in rows
    ]


async def latest_user_score(
    db: AsyncSession,
    user_id: str | UUID,
) -> dict | None:
    """
    Return the newest persisted score for one user.

    Supports either the internal UUID or the external user ID.
    """

    identifier = str(user_id).strip()

    if not identifier:
        return None

    conditions = [
        User.external_id == identifier,
    ]

    try:
        internal_id = UUID(identifier)
    except ValueError:
        internal_id = None

    if internal_id is not None:
        conditions.append(User.id == internal_id)

    statement = (
        select(
            ChurnScore,
            User.external_id,
            User.acquisition_channel,
            User.device_type,
        )
        .join(
            User,
            User.id == ChurnScore.user_id,
        )
        .where(or_(*conditions))
        .order_by(
            desc(ChurnScore.snapshot_date),
            desc(ChurnScore.scored_at),
        )
        .limit(1)
    )

    row = (await db.execute(statement)).first()

    if row is None:
        return None

    (
        score,
        external_id,
        acquisition_channel,
        device_type,
    ) = row

    return _score_payload(
        score,
        external_id,
        acquisition_channel,
        device_type,
    )


async def churn_summary(
    db: AsyncSession,
) -> dict:
    """Summarize the newest persisted scoring snapshot and model version."""

    risk_bands = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    context = await _latest_score_context(db)

    if context is None:
        return {
            "snapshot_date": None,
            "model_version": None,
            "total_scored": 0,
            "average_score": 0.0,
            "high_risk_count": 0,
            "risk_bands": risk_bands,
        }

    snapshot_date, model_version = context

    score_scope = (
        ChurnScore.snapshot_date == snapshot_date,
        ChurnScore.model_version == model_version,
    )

    aggregate = (
        await db.execute(
            select(
                func.count(ChurnScore.id),
                func.avg(ChurnScore.score),
            ).where(*score_scope)
        )
    ).one()

    total_scored = int(aggregate[0] or 0)
    average_score = float(aggregate[1] or 0.0)

    band_rows = (
        await db.execute(
            select(
                ChurnScore.risk_band,
                func.count(ChurnScore.id),
            )
            .where(*score_scope)
            .group_by(ChurnScore.risk_band)
        )
    ).all()

    for band, count in band_rows:
        if band in risk_bands:
            risk_bands[band] = int(count)

    return {
        "snapshot_date": snapshot_date,
        "model_version": model_version,
        "total_scored": total_scored,
        "average_score": average_score,
        "high_risk_count": (risk_bands["critical"] + risk_bands["high"]),
        "risk_bands": risk_bands,
    }


async def latest_model(
    db: AsyncSession,
) -> dict | None:
    """Return the latest persisted ModelRun."""

    model_run = await db.scalar(select(ModelRun).order_by(desc(ModelRun.trained_at)).limit(1))

    if model_run is None:
        return None

    return {
        "model_version": model_run.model_version,
        "algorithm": model_run.algorithm,
        "metrics": model_run.metrics,
        "feature_names": model_run.feature_names,
        "artifact_uri": model_run.artifact_uri,
        "trained_at": model_run.trained_at,
    }
