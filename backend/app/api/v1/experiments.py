from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_account
from app.db.models import Experiment, User
from app.db.session import get_db
from app.experiments.lifecycle import ExperimentLifecycleError
from app.schemas.experiment import (
    AssignmentResponse,
    ExperimentCreate,
    ExperimentResponse,
    ExperimentResults,
    ExposureResponse,
)
from app.services.experiment_service import (
    create_experiment,
    expose,
    get_or_assign,
    list_experiments,
    results,
)

router = APIRouter(
    prefix="/experiments",
    tags=["experiments"],
    dependencies=[Depends(get_current_account)],
)


async def _experiment(db: AsyncSession, experiment_id: UUID) -> Experiment:
    experiment = await db.get(Experiment, experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


async def _user(db: AsyncSession, user_id: UUID) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _lifecycle_conflict(exc: ExperimentLifecycleError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": exc.code, "message": str(exc)},
    )


@router.post("", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
async def create(payload: ExperimentCreate, db: AsyncSession = Depends(get_db)):
    return await create_experiment(db, payload)


@router.get("", response_model=list[ExperimentResponse])
async def list_all(db: AsyncSession = Depends(get_db)):
    return await list_experiments(db)


@router.post("/{experiment_id}/assign/{user_id}", response_model=AssignmentResponse)
async def assign(
    experiment_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    experiment = await _experiment(db, experiment_id)
    await _user(db, user_id)

    try:
        assignment = await get_or_assign(db, experiment, user_id)
    except ExperimentLifecycleError as exc:
        raise _lifecycle_conflict(exc) from exc

    return {
        "experiment_id": experiment_id,
        "user_id": user_id,
        "variant": assignment.variant,
    }


@router.post("/{experiment_id}/expose/{user_id}", response_model=ExposureResponse)
async def log_exposure(
    experiment_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    experiment = await _experiment(db, experiment_id)
    await _user(db, user_id)

    try:
        variant = await expose(db, experiment, user_id)
    except ExperimentLifecycleError as exc:
        raise _lifecycle_conflict(exc) from exc

    return {"variant": variant, "status": "exposed"}


@router.get("/{experiment_id}/results", response_model=ExperimentResults)
async def experiment_results(
    experiment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    experiment = await _experiment(db, experiment_id)
    return await results(db, experiment)
