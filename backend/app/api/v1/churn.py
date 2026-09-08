from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.api.deps import (
    get_current_account,
)
from app.db.session import get_db
from app.ml.predict import load_metadata
from app.services.churn_service import (
    churn_summary,
    latest_model,
    latest_scores,
    latest_user_score,
)


router = APIRouter(
    prefix="/churn",
    tags=["churn"],
    dependencies=[Depends(get_current_account)],
)


@router.get("/scores")
async def scores(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    risk_band: str | None = Query(
        default=None,
        pattern=("^(low|medium|high|critical)$"),
    ),
    acquisition_channel: str | None = Query(
        default=None,
        min_length=1,
        max_length=32,
    ),
    device_type: str | None = Query(
        default=None,
        min_length=1,
        max_length=16,
    ),
    db: AsyncSession = Depends(get_db),
):
    """Return latest persisted churn scores."""

    try:
        return await latest_scores(
            db,
            limit=limit,
            offset=offset,
            risk_band=risk_band,
            acquisition_channel=(acquisition_channel),
            device_type=device_type,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get("/scores/{user_id}")
async def user_score(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return the latest score for one user."""

    score = await latest_user_score(
        db,
        user_id,
    )

    if score is None:
        raise HTTPException(
            status_code=404,
            detail=("No churn score found for this user"),
        )

    return score


@router.get("/summary")
async def summary(
    db: AsyncSession = Depends(get_db),
):
    """Return latest scoring summary."""

    return await churn_summary(db)


@router.get("/model-health")
async def model_health(
    db: AsyncSession = Depends(get_db),
):
    """Return model lineage and health metadata."""

    model = await latest_model(db)

    if model is None:
        raise HTTPException(
            status_code=404,
            detail=("No model run is available"),
        )

    try:
        metadata = load_metadata()
    except (
        FileNotFoundError,
        KeyError,
        ValueError,
    ):
        metadata = {}

    return {
        "model_version": (model["model_version"]),
        "algorithm": (model["algorithm"]),
        "metrics": (model["metrics"]),
        "feature_names": (model["feature_names"]),
        "trained_at": (model["trained_at"]),
        "artifact_uri": (model["artifact_uri"]),
        "dataset": metadata.get("dataset"),
        "splits": metadata.get("splits"),
        "calibration": metadata.get("calibration"),
        "risk_bands": metadata.get("risk_bands"),
        "label_drift": metadata.get("label_drift"),
        "global_feature_importance": (
            metadata.get(
                "global_feature_importance",
                [],
            )
        ),
        "validation_candidates": (metadata.get("validation_candidates")),
    }
