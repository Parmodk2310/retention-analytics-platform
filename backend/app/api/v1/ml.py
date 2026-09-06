from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_account
from app.db.models import Account


router = APIRouter(prefix="/ml", tags=["machine-learning"])


class ChurnPredictionRequest(BaseModel):
    """Request contract for churn inference."""

    user_ids: list[str] | None = None
    top_n: int = Field(default=100, ge=1, le=1000)


@router.post("/churn/predict")
async def predict_churn(
    request: ChurnPredictionRequest,
    current_account: Account = Depends(get_current_account),
) -> None:
    """
    Churn inference is introduced in Phase 4.

    The API contract exists now so frontend and API consumers can be
    developed without pretending that a trained model is already available.
    """
    del request, current_account

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Churn prediction is not enabled yet. "
            "Model training, feature generation, artifact loading, "
            "and batch scoring are implemented in Phase 4."
        ),
    )


@router.get("/churn/user/{user_id}")
async def predict_single_user(
    user_id: str,
    current_account: Account = Depends(get_current_account),
) -> None:
    """Return a single-user churn score once Phase 4 is enabled."""
    del user_id, current_account

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Single-user churn prediction is not enabled yet. "
            "This endpoint becomes active after the Phase 4 ML pipeline."
        ),
    )
