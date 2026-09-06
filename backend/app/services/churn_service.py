from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChurnScore, ModelRun, User


async def latest_scores(
    db: AsyncSession, limit: int = 50, offset: int = 0, risk_band: str | None = None
) -> list[dict]:
    latest = await db.scalar(
        select(ChurnScore.snapshot_date).order_by(desc(ChurnScore.snapshot_date)).limit(1)
    )
    if latest is None:
        return []
    stmt = (
        select(ChurnScore, User.external_id)
        .join(User, User.id == ChurnScore.user_id)
        .where(ChurnScore.snapshot_date == latest)
        .order_by(desc(ChurnScore.score))
        .limit(limit)
        .offset(offset)
    )
    if risk_band:
        stmt = stmt.where(ChurnScore.risk_band == risk_band)
    rows = (await db.execute(stmt)).all()
    return [
        {
            "user_id": s.user_id,
            "external_id": external,
            "snapshot_date": s.snapshot_date,
            "score": s.score,
            "risk_band": s.risk_band,
            "model_version": s.model_version,
            "reasons": s.reasons,
        }
        for s, external in rows
    ]


async def latest_model(db: AsyncSession) -> ModelRun | None:
    return await db.scalar(select(ModelRun).order_by(desc(ModelRun.trained_at)).limit(1))
