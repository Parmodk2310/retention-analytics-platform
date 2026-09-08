import json
import joblib
import numpy as np
from datetime import UTC, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import ModelRun
from app.ml.artifact_store import upload_artifact
from app.ml.dataset import build_training_dataset
from app.ml.evaluate import evaluate_binary
from app.ml.features import FEATURES
from app.ml.explain import global_feature_importance
from app.ml.pipeline import logistic_pipeline, xgboost_pipeline
from app.ml.threshold import choose_threshold
from app.ml.calibration import fit_sigmoid_calibrator
from app.ml.split import (
    split_metadata,
    temporal_fit_calibration_split,
    temporal_train_validation_test_split,
)
from app.ml.lineage import archive_latest_artifacts


def train() -> dict:
    """Train, select, refit, evaluate, and persist the churn model."""

    engine = create_engine(
        settings.DATABASE_URL_SYNC,
        pool_pre_ping=True,
    )

    # ---------------------------------------------------------
    # 1. Build temporal dataset
    # ---------------------------------------------------------

    df = build_training_dataset(engine)

    if df.empty:
        raise RuntimeError("Training dataset is empty")

    # ---------------------------------------------------------
    # 2. Temporal train / validation / test split
    # ---------------------------------------------------------

    splits = temporal_train_validation_test_split(df)

    calibration_split = temporal_fit_calibration_split(splits.train)
    fit_df = calibration_split.fit
    calibration_df = calibration_split.calibration
    validation_df = splits.validation
    test_df = splits.test

    X_fit = fit_df[FEATURES]
    y_fit = fit_df["churned"]
    X_calibration = calibration_df[FEATURES]
    y_calibration = calibration_df["churned"]

    X_validation = validation_df[FEATURES]
    y_validation = validation_df["churned"]

    X_test = test_df[FEATURES]
    y_test = test_df["churned"]

    # ---------------------------------------------------------
    # 3. Calculate training imbalance
    # ---------------------------------------------------------

    scale_pos_weight = float((y_fit == 0).sum() / max((y_fit == 1).sum(), 1))

    # ---------------------------------------------------------
    # 4. Create fresh model builders
    # ---------------------------------------------------------

    candidate_builders = {
        "logistic_regression": lambda: logistic_pipeline(),
        "xgboost": lambda: xgboost_pipeline(scale_pos_weight),
    }

    # ---------------------------------------------------------
    # 5. Train candidates on TRAIN only
    #    Evaluate candidates on VALIDATION only
    # ---------------------------------------------------------

    validation_metrics = {}
    calibrated_candidates = {}

    for name, builder in candidate_builders.items():
        base_model = builder()
        base_model.fit(X_fit, y_fit)
        calibrated_model = fit_sigmoid_calibrator(base_model, X_calibration, y_calibration)
        raw_probability = base_model.predict_proba(X_validation)[:, 1]
        calibrated_probability = calibrated_model.predict_proba(X_validation)[:, 1]
        validation_metrics[name] = {
            "uncalibrated": evaluate_binary(y_validation, raw_probability),
            "calibrated": evaluate_binary(y_validation, calibrated_probability),
        }
        calibrated_candidates[name] = calibrated_model

    # ---------------------------------------------------------
    # 6. Select best algorithm using validation PR-AUC
    # ---------------------------------------------------------

    best_name = max(
        validation_metrics,
        key=lambda name: (
            validation_metrics[name]["calibrated"]["roc_auc"],
            validation_metrics[name]["calibrated"]["normalized_pr_auc"],
            -validation_metrics[name]["calibrated"]["brier"],
        ),
    )

    final_model = calibrated_candidates[best_name]

    # ---------------------------------------------------------
    # 7. Select decision threshold using VALIDATION only
    # ---------------------------------------------------------

    validation_probability = final_model.predict_proba(X_validation)[:, 1]

    decision_threshold, threshold_table = choose_threshold(
        y_validation,
        validation_probability,
    )

    # ---------------------------------------------------------
    # 12. Evaluate ONCE on untouched TEST data
    # ---------------------------------------------------------

    test_probability = final_model.predict_proba(X_test)[:, 1]

    test_metrics = evaluate_binary(
        y_test,
        test_probability,
        threshold=decision_threshold,
    )

    # ---------------------------------------------------------
    # 13. Generate model version
    # ---------------------------------------------------------

    version = datetime.now(UTC).strftime("churn_%Y%m%dT%H%M%SZ")

    # ---------------------------------------------------------
    # 14. Prepare artifact directory
    # ---------------------------------------------------------

    settings.MODEL_ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_path = settings.MODEL_ARTIFACT_DIR / "churn_model.joblib"

    meta_path = settings.MODEL_ARTIFACT_DIR / "model_metadata.json"

    # ---------------------------------------------------------
    # 15. Save final model
    # ---------------------------------------------------------

    joblib.dump(
        final_model,
        model_path,
    )

    train_prevalence = float(splits.train["churned"].mean())

    validation_prevalence = float(validation_df["churned"].mean())

    test_prevalence = float(test_df["churned"].mean())

    artifact_uri = upload_artifact(
        model_path,
        (f"models/{version}/churn_model.joblib"),
    )

    upload_artifact(
        meta_path,
        (f"models/{version}/model_metadata.json"),
    )

    upload_artifact(
        model_path,
        "models/latest/churn_model.joblib",
    )

    upload_artifact(
        meta_path,
        "models/latest/model_metadata.json",
    )
    # ---------------------------------------------------------
    # 16. Build model metadata
    # ---------------------------------------------------------

    metadata = {
        "model_version": version,
        "algorithm": best_name,
        "decision_threshold": decision_threshold,
        "global_feature_importance": global_feature_importance(final_model),
        "features": FEATURES,
        "trained_at": datetime.now(UTC).isoformat(),
        "dataset": {
            "feature_window_days": 90,
            "label_window_days": 30,
            "snapshot_count": int(df["snapshot_date"].nunique()),
        },
        "splits": split_metadata(splits),
        "calibration": {
            "method": "sigmoid_platt",
            "fit_rows": int(len(fit_df)),
            "calibration_rows": int(len(calibration_df)),
            "calibration_snapshot": calibration_df["snapshot_date"].max().date().isoformat(),
        },
        "risk_bands": {
            "method": "validation_score_quantiles",
            "thresholds": {
                "critical": float(np.quantile(validation_probability, 0.95)),
                "high": float(np.quantile(validation_probability, 0.80)),
                "medium": float(np.quantile(validation_probability, 0.50)),
            },
        },
        "label_drift": {
            "train_prevalence": train_prevalence,
            "validation_prevalence": validation_prevalence,
            "test_prevalence": test_prevalence,
            "train_to_test_pp": float((test_prevalence - train_prevalence) * 100),
        },
        "validation_candidates": validation_metrics,
        "test_metrics": test_metrics,
        "threshold_search": threshold_table,
    }

    # ---------------------------------------------------------
    # 17. Save metadata
    # ---------------------------------------------------------

    meta_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # 22. Persist model run in database
    # ---------------------------------------------------------

    with Session(engine) as session:
        session.add(
            ModelRun(
                model_version=version,
                algorithm=best_name,
                metrics=test_metrics,
                feature_names=FEATURES,
                artifact_uri=artifact_uri,
            )
        )

        session.commit()

    # ---------------------------------------------------------
    # 23. Return metadata
    # ---------------------------------------------------------
    archive_latest_artifacts()
    return metadata


if __name__ == "__main__":
    print(
        json.dumps(
            train(),
            indent=2,
            default=str,
        )
    )
