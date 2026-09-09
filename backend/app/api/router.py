from fastapi import APIRouter

from app.api.v1 import analytics, auth, churn, events, experiments, health, system

api_router = APIRouter()
for router in [
    health.router,
    auth.router,
    events.router,
    analytics.router,
    churn.router,
    experiments.router,
    system.router,
]:
    api_router.include_router(router)
