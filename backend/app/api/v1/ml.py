from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_account
from app.db.session import get_db
from app.db.models import Account


router = APIRouter(prefix="/ml", tags=["machine-learning"])


class ChurnPredictionRequest(BaseModel):
    user_ids: list[int] | None = None  # None = all users
    top_n: int = 100  # Return top N highest risk


class RetrainRequest(BaseModel):
    test_size: float = 0.2
    model_type: str = "xgboost"  # xgboost | random_forest | logistic


@router.post("/churn/predict")
async def predict_churn(
    req: ChurnPredictionRequest,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_account),
):
    """Predict churn probability for users."""
    predictor = get_predictor()

    try:
        results = predictor.predict(db, req.user_ids)
        return {
            "predictions": results[: req.top_n],
            "total_scored": len(results),
            "high_risk_count": sum(1 for r in results if r["risk_level"] == "high"),
        }
    except Exception as exc:
        raise HTTPException(
        status_code=500,
        detail=f"Prediction failed: {exc}",
    ) from exc


@router.get("/churn/user/{user_id}")
async def predict_single_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_account),
):

    predictor = get_predictor()
    result = predictor.predict_single(db, user_id)

    if "error" in result:
        raise HTTPException(404, result["error"])
    return result
