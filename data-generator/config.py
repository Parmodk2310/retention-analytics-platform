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

DATABASE_URL = os.getenv(
    "DATABASE_URL_SYNC",
    "postgresql+psycopg://retention:retention@localhost:5432/retention",
).replace("postgresql+psycopg://", "postgresql://")

END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=365)

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

# Stable namespaces make generated IDs reproducible across reruns with the same seed.
USER_NAMESPACE = uuid.UUID("d4f0de31-1113-4db9-8b89-5f7b8184b001")
SESSION_NAMESPACE = uuid.UUID("d4f0de31-1113-4db9-8b89-5f7b8184b002")
EVENT_NAMESPACE = uuid.UUID("d4f0de31-1113-4db9-8b89-5f7b8184b003")
