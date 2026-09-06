import uuid
from datetime import timedelta

import numpy as np

from config import CHANNELS, COUNTRIES, DEVICES, END_DATE, N_USERS, SEED, USER_NAMESPACE

CHANNEL_QUALITY = {
    "organic": 0.75,
    "referral": 0.70,
    "email": 0.62,
    "affiliate": 0.55,
    "paid_social": 0.45,
}


def generate_users(rng: np.random.Generator) -> list[dict]:
    channels = list(CHANNELS)
    weights = list(CHANNELS.values())
    rows: list[dict] = []

    # Slightly bias toward older signups so 12-month cohorts are populated.
    ages = np.clip(rng.beta(1.15, 1.0, N_USERS) * 365, 0, 364).astype(int)

    for i, age in enumerate(ages, 1):
        external_id = f"usr_{i:06d}"
        # Deterministic IDs make the seed idempotent and reproducible.
        user_id = uuid.uuid5(USER_NAMESPACE, f"seed={SEED}:{external_id}")

        channel = str(rng.choice(channels, p=weights))
        device = str(rng.choice(DEVICES, p=[0.38, 0.42, 0.20]))
        country = str(rng.choice(COUNTRIES, p=[0.65, 0.13, 0.08, 0.06, 0.08]))

        engagement = float(
            np.clip(
                rng.beta(3, 2) * 0.65 + CHANNEL_QUALITY[channel] * 0.35,
                0.05,
                0.98,
            )
        )
        signup = END_DATE - timedelta(days=int(age))

        rows.append(
            {
                "id": user_id,
                "external_id": external_id,
                "signup_date": signup,
                "acquisition_channel": channel,
                "device_type": device,
                "country": country,
                "baseline_engagement": engagement,
            }
        )

    return rows
