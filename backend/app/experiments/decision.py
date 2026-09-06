def recommend(srm:dict,analysis:dict|None,guardrail_ok:bool=True)->str:
    if srm.get("detected"):return "investigate_srm"
    if not guardrail_ok:return "do_not_ship_guardrail_regression"
    if not analysis:return "collect_more_data"
    if analysis["significant"] and analysis["absolute_lift"]>0:return "ship_treatment"
    if analysis["significant"] and analysis["absolute_lift"]<0:return "stop_treatment"
    return "inconclusive_collect_more_data"
