from datetime import UTC,datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Experiment,ExperimentAssignment,ExperimentExposure,User
from app.experiments.assignment import assign_variant
from app.experiments.decision import recommend
from app.experiments.metrics import binary_conversion_counts
from app.experiments.srm import sample_ratio_mismatch
from app.experiments.stats import analyze_binary
from app.schemas.experiment import ExperimentCreate

async def create_experiment(db:AsyncSession,payload:ExperimentCreate)->Experiment:
    obj=Experiment(**payload.model_dump());db.add(obj);await db.commit();await db.refresh(obj);return obj
async def list_experiments(db:AsyncSession)->list[Experiment]: return list((await db.scalars(select(Experiment).order_by(Experiment.created_at.desc()))).all())
async def get_or_assign(db:AsyncSession,experiment:Experiment,user_id:UUID)->ExperimentAssignment:
    existing=await db.scalar(select(ExperimentAssignment).where(ExperimentAssignment.experiment_id==experiment.id,ExperimentAssignment.user_id==user_id))
    if existing:return existing
    variant=assign_variant(str(user_id),str(experiment.id),experiment.traffic_allocation)
    stmt=insert(ExperimentAssignment).values(experiment_id=experiment.id,user_id=user_id,variant=variant).on_conflict_do_nothing(constraint="uq_assignment_experiment_user").returning(ExperimentAssignment.id)
    await db.execute(stmt);await db.commit()
    return await db.scalar(select(ExperimentAssignment).where(ExperimentAssignment.experiment_id==experiment.id,ExperimentAssignment.user_id==user_id))
async def expose(db:AsyncSession,experiment:Experiment,user_id:UUID)->str:
    assignment=await get_or_assign(db,experiment,user_id)
    stmt=insert(ExperimentExposure).values(experiment_id=experiment.id,user_id=user_id,variant=assignment.variant,exposed_at=datetime.now(UTC)).on_conflict_do_nothing(constraint="uq_exposure_experiment_user")
    await db.execute(stmt);await db.commit();return assignment.variant
async def results(db:AsyncSession,experiment:Experiment)->dict:
    counts=await binary_conversion_counts(db,str(experiment.id),"purchase",14)
    observed={k:v["n"] for k,v in counts.items()};srm=sample_ratio_mismatch(observed,experiment.traffic_allocation)
    analysis=None
    variants=list(experiment.traffic_allocation)
    if len(variants)==2 and all(k in counts for k in variants):
        c,t=variants[0],variants[1];analysis=analyze_binary(counts[c]["conversions"],counts[c]["n"],counts[t]["conversions"],counts[t]["n"])
    rates={k:(v["conversions"]/v["n"] if v["n"] else 0.0) for k,v in counts.items()}
    return {"experiment_id":experiment.id,"counts":observed,"conversion_rates":rates,"srm":srm,"analysis":analysis,"decision":recommend(srm,analysis)}
