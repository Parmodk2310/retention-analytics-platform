from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_account
from app.db.models import Experiment, User
from app.db.session import get_db
from app.schemas.experiment import AssignmentResponse, ExperimentCreate, ExperimentResponse
from app.services.experiment_service import (
    create_experiment,
    expose,
    get_or_assign,
    list_experiments,
    results,
)

router = APIRouter(
    prefix="/experiments", tags=["experiments"], dependencies=[Depends(get_current_account)]
)


@router.post("", response_model=ExperimentResponse, status_code=201)
async def create(payload: ExperimentCreate, db: AsyncSession = Depends(get_db)):
    return await create_experiment(db, payload)


@router.get("", response_model=list[ExperimentResponse])
async def list_all(db: AsyncSession = Depends(get_db)):
    return await list_experiments(db)


async def _exp(db: AsyncSession, experiment_id: UUID) -> Experiment:
    obj = await db.get(Experiment, experiment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return obj


@router.post("/{experiment_id}/assign/{user_id}", response_model=AssignmentResponse)
async def assign(experiment_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db)):
    exp = await _exp(db, experiment_id)
    if not await db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    a = await get_or_assign(db, exp, user_id)
    return {"experiment_id": experiment_id, "user_id": user_id, "variant": a.variant}


@router.post("/{experiment_id}/expose/{user_id}")
async def log_exposure(experiment_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db)):
    exp = await _exp(db, experiment_id)
    variant = await expose(db, exp, user_id)
    return {"variant": variant, "status": "exposed"}


@router.get("/{experiment_id}/results")
async def experiment_results(experiment_id: UUID, db: AsyncSession = Depends(get_db)):
    exp = await _exp(db, experiment_id)
    return await results(db, exp)
