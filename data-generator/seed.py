#!/usr/bin/env python3
"""
Synthetic Data Generator
Generates 1M+ events across 50K users over 12 months with realistic patterns.
"""
import os
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass

import numpy as np
import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# ─── Configuration ──────────────────────────────────────────────────────────
N_USERS = 50_000
N_EVENTS = 1_200_000  # ~24 events per user average
MONTHS_HISTORY = 12
END_DATE = datetime(2026, 8, 15)
START_DATE = END_DATE - timedelta(days=30 * MONTHS_HISTORY)

# Channel configs: (weight, retention_multiplier, revenue_multiplier)
CHANNEL_CONFIG = {
    "organic":      (0.30, 1.40, 1.20),
    "paid_social":  (0.25, 0.85, 0.90),
    "referral":     (0.15, 1.60, 1.50),
    "email":        (0.20, 1.10, 1.00),
    "affiliate":    (0.10, 0.70, 0.75),
}

DEVICE_TYPES = ["ios", "android", "web"]
DEVICE_WEIGHTS = [0.35, 0.40, 0.25]

EVENT_TYPES = ["page_view", "search", "add_to_cart", "checkout", "purchase", "session_start"]
EVENT_WEIGHTS = [0.40, 0.20, 0.15, 0.10, 0.08, 0.07]

# A/B Test: Onboarding experiment
EXPERIMENT_ID = "exp_onboarding_v2"
VARIANTS = ["control", "treatment"]


@dataclass
class User:
    user_id: int
    signup_date: datetime
    acquisition_channel: str
    device_type: str
    experiment_variant: str
    initial_ltv: float


@dataclass
class Event:
    event_id: str
    user_id: int
    event_type: str
    timestamp: datetime
    session_id: str
    revenue: float
    properties: Dict


class DataGenerator:
    def __init__(self):
        self.users: List[User] = []
        self.events: List[Event] = []
        self.sessions: Dict[int, List[Dict]] = {}  # user_id -> sessions

    def _assign_variant(self, user_id: int) -> str:
        """Deterministic hash-based assignment."""
        hash_val = hash(f"{EXPERIMENT_ID}:{user_id}") % 100
        return "treatment" if hash_val < 50 else "control"

    def _generate_ltv(self, channel: str) -> float:
        base = np.random.exponential(30)
        multiplier = CHANNEL_CONFIG[channel][2]
        return round(base * multiplier, 2)

    def generate_users(self) -> pd.DataFrame:
        print(f"🧑 Generating {N_USERS:,} users...")
        channels = list(CHANNEL_CONFIG.keys())
        channel_weights = [c[0] for c in CHANNEL_CONFIG.values()]

        for i in tqdm(range(1, N_USERS + 1), desc="Users"):
            channel = np.random.choice(channels, p=channel_weights)
            user = User(
                user_id=i,
                signup_date=fake.date_time_between(START_DATE, END_DATE),
                acquisition_channel=channel,
                device_type=np.random.choice(DEVICE_TYPES, p=DEVICE_WEIGHTS),
                experiment_variant=self._assign_variant(i),
                initial_ltv=self._generate_ltv(channel),
            )
            self.users.append(user)

        df = pd.DataFrame([u.__dict__ for u in self.users])
        return df

    def _generate_session_events(self, user: User, n_events: int) -> List[Event]:
        """Generate a realistic session with correlated events."""
        session_start = fake.date_time_between(
            max(user.signup_date, END_DATE - timedelta(days=30)), END_DATE
        )
        session_id = str(uuid.uuid4())[:12]

        # Channel affects session depth
        depth_multiplier = CHANNEL_CONFIG[user.acquisition_channel][1]
        base_depth = np.random.poisson(5 * depth_multiplier)
        n_session_events = min(n_events, max(2, base_depth))

        events = []
        # Always start with session_start
        events.append(Event(
            event_id=str(uuid.uuid4()),
            user_id=user.user_id,
            event_type="session_start",
            timestamp=session_start,
            session_id=session_id,
            revenue=0.0,
            properties={"page": "home", "referrer": user.acquisition_channel}
        ))

        # Funnel progression with realistic drop-offs
        funnel_steps = ["page_view", "search", "add_to_cart", "checkout", "purchase"]
        funnel_probs = [1.0, 0.55, 0.30, 0.18, 0.12]  # Drop-off rates

        current_time = session_start
        for i in range(1, n_session_events):
            current_time += timedelta(seconds=random.randint(30, 300))

            # Decide event type based on funnel position
            if i < len(funnel_steps):
                if random.random() < funnel_probs[i]:
                    event_type = funnel_steps[i]
                else:
                    event_type = random.choices(
                        ["page_view", "search"], weights=[0.6, 0.4]
                    )[0]
            else:
                event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS)[0]

            revenue = 0.0
            if event_type == "purchase":
                revenue = round(np.random.exponential(45) * (1.15 if user.experiment_variant == "treatment" else 1.0), 2)

            events.append(Event(
                event_id=str(uuid.uuid4()),
                user_id=user.user_id,
                event_type=event_type,
                timestamp=current_time,
                session_id=session_id,
                revenue=revenue,
                properties={
                    "page": random.choice(["home", "product", "cart", "checkout"]),
                    "variant": user.experiment_variant,
                }
            ))

        return events

    def generate_events(self) -> pd.DataFrame:
        print(f"📊 Generating {N_EVENTS:,} events...")
        events_per_user = np.random.poisson(N_EVENTS / N_USERS, N_USERS)

        for user, n_events in tqdm(zip(self.users, events_per_user), total=N_USERS, desc="Events"):
            # Generate multiple sessions per user
            n_sessions = max(1, int(n_events / 5))
            events_remaining = n_events

            for _ in range(n_sessions):
                if events_remaining <= 0:
                    break
                session_events = self._generate_session_events(user, min(events_remaining, 15))
                self.events.extend(session_events)
                events_remaining -= len(session_events)

        df = pd.DataFrame([e.__dict__ for e in self.events])
        return df

    def seed_database(self, db_url: str):
        """Seed PostgreSQL with generated data."""
        engine = create_engine(db_url)
        
        print("📦 Seeding database...")
        with engine.begin() as conn:
            # Clear existing
            conn.execute(text("TRUNCATE TABLE events, users CASCADE;"))
            
            users_df = self.generate_users()
            users_df.to_sql("users", conn, if_exists="append", index=False)
            
            self.generate_events()
            events_df = pd.DataFrame([e.__dict__ for e in self.events])
            events_df.to_sql("events", conn, if_exists="append", index=False)
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_events_user_timestamp 
                ON events(user_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_events_type_timestamp 
                ON events(event_type, timestamp);
                CREATE INDEX IF NOT EXISTS idx_users_channel 
                ON users(acquisition_channel);
                CREATE INDEX IF NOT EXISTS idx_users_signup 
                ON users(signup_date);
            """))
            
        print(f"✅ Seeded {len(self.users):,} users and {len(self.events):,} events.")


if __name__ == "__main__":
    DB_URL = os.getenv("DATABASE_URL", "postgresql://analytics:analytics_dev@localhost:5432/retention_db")
    gen = DataGenerator()
    gen.seed_database(DB_URL)