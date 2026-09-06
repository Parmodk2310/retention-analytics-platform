from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.ml.predict import get_predictor

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
    current_user: int = Depends(get_current_user),
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
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")


@router.get("/churn/user/{user_id}")
async def predict_single_user(
    user_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)
):
    """Predict churn for a single user."""
    predictor = get_predictor()
    result = predictor.predict_single(db, user_id)

    if "error" in result:
        raise HTTPException(404, result["error"])
    return result
