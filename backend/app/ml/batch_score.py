import json
from collections import Counter
from datetime import date
from uuid import UUID

from sqlalchemy import create_engine, func
from sqlalchemy.dialects.postgresql import (
    insert as postgres_insert,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ChurnScore
from app.ml.dataset import (
    build_feature_snapshot,
    latest_scoring_snapshot_date,
)
from app.ml.explain import (
    shap_reason_codes,
)
from app.ml.features import FEATURES
from app.ml.predict import (
    load_metadata,
    load_model,
    risk_band_from_metadata,
)


DEFAULT_CHUNK_SIZE = 2000


def _upsert_scores(
    session: Session,
    rows: list[dict],
) -> None:
    if not rows:
        return

    statement = postgres_insert(ChurnScore).values(rows)

    statement = statement.on_conflict_do_update(
        constraint="uq_churn_score",
        set_={
            "score": statement.excluded.score,
            "risk_band": statement.excluded.risk_band,
            "reasons": statement.excluded.reasons,
            "scored_at": func.now(),
        },
    )

    session.execute(statement)


def score_users(
    snapshot_date: date | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> dict:
    """
    Score all eligible users for the newest
    production feature snapshot.

    The operation is idempotent because churn_scores
    is upserted using its unique score constraint.
    """

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive.")

    engine = create_engine(
        settings.DATABASE_URL_SYNC,
        pool_pre_ping=True,
    )

    scoring_date = snapshot_date or latest_scoring_snapshot_date(engine)

    frame = build_feature_snapshot(
        engine,
        snapshot_date=scoring_date,
    )

    if frame.empty:
        raise RuntimeError("Production scoring snapshot is empty.")

    model = load_model()
    metadata = load_metadata()

    model_version = metadata.get("model_version")

    if not model_version:
        raise RuntimeError("Model metadata is missing model_version.")

    scored_count = 0
    band_counts: Counter[str] = Counter()

    with Session(engine) as session:
        for start in range(
            0,
            len(frame),
            chunk_size,
        ):
            stop = min(
                start + chunk_size,
                len(frame),
            )

            batch = frame.iloc[start:stop].copy().reset_index(drop=True)

            probabilities = model.predict_proba(batch[FEATURES])[:, 1]

            reasons = shap_reason_codes(
                model,
                batch,
                top_n=3,
            )

            rows = []

            for index, probability in enumerate(probabilities):
                score = float(probability)

                band = risk_band_from_metadata(
                    score,
                    metadata,
                )

                user_id = UUID(str(batch.iloc[index]["user_id"]))

                rows.append(
                    {
                        "user_id": user_id,
                        "snapshot_date": scoring_date,
                        "score": score,
                        "risk_band": band,
                        "model_version": model_version,
                        "reasons": reasons[index],
                    }
                )

                band_counts[band] += 1

            _upsert_scores(
                session,
                rows,
            )

            session.commit()

            scored_count += len(rows)

            print(f"Scored {scored_count}/{len(frame)} users")

    return {
        "snapshot_date": (scoring_date.isoformat()),
        "model_version": (model_version),
        "users_scored": (scored_count),
        "risk_bands": {
            "critical": band_counts["critical"],
            "high": band_counts["high"],
            "medium": band_counts["medium"],
            "low": band_counts["low"],
        },
    }


if __name__ == "__main__":
    print(
        json.dumps(
            score_users(),
            indent=2,
        )
    )
