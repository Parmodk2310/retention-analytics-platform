def churn_label(future_activity_count:int)->int:
    """Churn means no qualifying session/purchase activity in the FUTURE label window."""
    return int(future_activity_count==0)
