import os
import uuid
from datetime import date, timedelta

N_USERS = int(os.getenv("GENERATOR_USERS", "50000"))
TARGET_EVENTS = int(os.getenv("TARGET_EVENTS", "1200000"))
SEED = int(os.getenv("GENERATOR_SEED", "42"))
RESET_ANALYTICS_DATA = os.getenv("RESET_ANALYTICS_DATA", "false").lower() in {
    "1",
    "true",
    "yes",
}

DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")

if not DATABASE_URL_SYNC:
    raise RuntimeError(
        "DATABASE_URL_SYNC must be provided through the environment"
    )

DATABASE_URL = DATABASE_URL_SYNC.replace(
    "postgresql+psycopg://",
    "postgresql://",
)

# Pinning this via GENERATOR_END_DATE makes the dataset reproducible across days.
END_DATE = date.fromisoformat(os.getenv("GENERATOR_END_DATE", date.today().isoformat()))
START_DATE = END_DATE - timedelta(days=365)

# Calibrated so 5k users produce roughly 120k events while preserving the
# channel-retention relationship over the full 12-month lifecycle.
ACTIVITY_SCALE = float(os.getenv("GENERATOR_ACTIVITY_SCALE", "0.076"))

CHANNELS = {
    "organic": 0.30,
    "paid_social": 0.25,
    "referral": 0.15,
    "email": 0.20,
    "affiliate": 0.10,
}
DEVICES = ["ios", "android", "web"]
COUNTRIES = ["IN", "US", "GB", "DE", "SG"]

EXPERIMENT_ID = "11111111-1111-4111-8111-111111111111"
EXPERIMENT_KEY = "onboarding_v2"
EXPERIMENT_SALT = "retention-analytics-v1"

USER_NAMESPACE = uuid.UUID("d4f0de31-1113-4db9-8b89-5f7b8184b001")
SESSION_NAMESPACE = uuid.UUID("d4f0de31-1113-4db9-8b89-5f7b8184b002")
EVENT_NAMESPACE = uuid.UUID("d4f0de31-1113-4db9-8b89-5f7b8184b003")
