import json

from sqlalchemy import create_engine, text

from app.core.config import settings


def status() -> dict:
    engine = create_engine(settings.DATABASE_URL_SYNC, pool_pre_ping=True)
    with engine.connect() as connection:
        model = (
            connection.execute(
                text(
                    "SELECT model_version, algorithm, metrics, trained_at FROM model_runs ORDER BY trained_at DESC LIMIT 1"
                )
            )
            .mappings()
            .first()
        )
        scores = (
            connection.execute(
                text(
                    "SELECT MAX(snapshot_date) snapshot_date, COUNT(*) score_count FROM churn_scores"
                )
            )
            .mappings()
            .one()
        )
    if model is None:
        return {"status": "missing_model", "score_count": int(scores["score_count"])}
    metrics = model["metrics"]
    alerts = []
    if float(metrics.get("brier_skill_score", 0)) <= 0:
        alerts.append("Model probabilities do not beat the prevalence baseline")
    if float(metrics.get("roc_auc", 0)) < 0.70:
        alerts.append("ROC-AUC below 0.70")
    if int(scores["score_count"]) == 0:
        alerts.append("No persisted churn scores")
    return {
        "status": "alert" if alerts else "ok",
        "alerts": alerts,
        "model_version": model["model_version"],
        "algorithm": model["algorithm"],
        "metrics": metrics,
        "trained_at": model["trained_at"].isoformat(),
        "latest_score_date": scores["snapshot_date"].isoformat()
        if scores["snapshot_date"]
        else None,
        "score_count": int(scores["score_count"]),
    }


if __name__ == "__main__":
    print(json.dumps(status(), indent=2, default=str))
