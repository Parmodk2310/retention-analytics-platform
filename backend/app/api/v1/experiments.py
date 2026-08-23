import hashlib
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.api.deps import get_db, get_current_user
from app.db.models import Experiment, ExperimentAssignment, User, Event
from app.experiments.stats import ABTestAnalyzer

router = APIRouter(prefix="/experiments", tags=["experiments"])


class ExperimentCreate(BaseModel):
    experiment_id: str
    name: str
    hypothesis: str
    metric_type: str = "proportion"  # proportion | continuous


class ExperimentResult(BaseModel):
    experiment_id: str
    status: str
    control_conversions: int
    control_size: int
    treatment_conversions: int
    treatment_size: int
    analysis: dict


@router.post("/")
async def create_experiment(
    data: ExperimentCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """Create a new experiment."""
    exp = Experiment(
        experiment_id=data.experiment_id,
        name=data.name,
        hypothesis=data.hypothesis,
        metric_type=data.metric_type,
        start_date=datetime.utcnow()
    )
    db.add(exp)
    db.commit()
    return {"message": "Experiment created", "experiment_id": data.experiment_id}


@router.get("/{exp_id}/assign/{user_id}")
async def assign_variant(
    exp_id: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Assign user to variant. Deterministic — same user always gets same variant.
    Used by client SDKs at app startup.
    """
    # Check if already assigned
    existing = db.query(ExperimentAssignment).filter_by(
        experiment_id=exp_id, user_id=user_id
    ).first()
    
    if existing:
        return {"variant": existing.variant, "assigned_at": existing.assigned_at}
    
    # Deterministic assignment
    hash_val = int(hashlib.md5(f"{exp_id}:{user_id}".encode()).hexdigest(), 16)
    variant = "treatment" if (hash_val % 100) < 50 else "control"
    
    assignment = ExperimentAssignment(
        experiment_id=exp_id,
        user_id=user_id,
        variant=variant
    )
    db.add(assignment)
    db.commit()
    
    return {"variant": variant, "assigned_at": datetime.utcnow()}


@router.get("/{exp_id}/results")
async def get_results(
    exp_id: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Analyze experiment results.
    For proportion metrics: Z-test on conversion rates.
    """
    exp = db.query(Experiment).filter_by(experiment_id=exp_id).first()
    if not exp:
        raise HTTPException(404, "Experiment not found")
    
    # Fetch assignments joined with conversion events
    query = text("""
        SELECT 
            ea.variant,
            COUNT(DISTINCT ea.user_id) as users,
            COUNT(DISTINCT CASE WHEN e.event_type = 'purchase' THEN e.user_id END) as conversions,
            COALESCE(SUM(e.revenue), 0) as total_revenue
        FROM experiment_assignments ea
        LEFT JOIN events e ON ea.user_id = e.user_id 
            AND e.timestamp >= ea.assigned_at
            AND e.event_type IN ('purchase', 'session_start')
        WHERE ea.experiment_id = :exp_id
        GROUP BY ea.variant
    """)
    
    rows = db.execute(query, {"exp_id": exp_id}).mappings().all()
    data = {r["variant"]: dict(r) for r in rows}
    
    if "control" not in data or "treatment" not in data:
        return {"error": "Insufficient data — both variants need users"}
    
    analyzer = ABTestAnalyzer(alpha=0.05)
    
    if exp.metric_type == "proportion":
        result = analyzer.analyze_proportions(
            control_conversions=data["control"]["conversions"],
            control_size=data["control"]["users"],
            treatment_conversions=data["treatment"]["conversions"],
            treatment_size=data["treatment"]["users"]
        )
    else:
        # For continuous metrics, we'd need raw value arrays
        result = {"error": "Continuous metric analysis requires raw data endpoint"}
    
    return {
        "experiment_id": exp_id,
        "hypothesis": exp.hypothesis,
        "metric_type": exp.metric_type,
        "status": exp.status,
        "sample_sizes": {
            "control": data["control"]["users"],
            "treatment": data["treatment"]["users"]
        },
        "analysis": result.__dict__ if hasattr(result, '__dict__') else result
    }


@router.post("/{exp_id}/conclude")
async def conclude_experiment(
    exp_id: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """Mark experiment as concluded."""
    exp = db.query(Experiment).filter_by(experiment_id=exp_id).first()
    if not exp:
        raise HTTPException(404, "Experiment not found")
    
    exp.status = "concluded"
    exp.end_date = datetime.utcnow()
    db.commit()
    
    return {"message": f"Experiment {exp_id} concluded"}