from datetime import date

from sqlalchemy import create_engine

from app.core.config import settings
from app.ml.dataset import build_snapshot
from app.ml.explain import (
    global_feature_importance,
    shap_reason_codes,
)
from app.ml.predict import load_model


def main() -> None:
    engine = create_engine(
        settings.DATABASE_URL_SYNC,
        pool_pre_ping=True,
    )

    frame = build_snapshot(
        engine,
        snapshot_date=date(2026, 8, 8),
        label_days=30,
    )

    sample = frame.sample(
        n=5,
        random_state=42,
    ).reset_index(drop=True)

    model = load_model()

    print("=== GLOBAL IMPORTANCE ===")

    for item in global_feature_importance(
        model,
        top_n=10,
    ):
        print(item)

    print()
    print("=== LOCAL SHAP REASONS ===")

    reasons = shap_reason_codes(
        model,
        sample,
        top_n=3,
    )

    scores = model.predict_proba(sample)[:, 1]

    for index, reason_list in enumerate(reasons):
        print()
        print(
            "User:",
            sample.iloc[index]["user_id"],
        )
        print(
            "Score:",
            round(float(scores[index]), 4),
        )

        for reason in reason_list:
            print(reason)


if __name__ == "__main__":
    main()
