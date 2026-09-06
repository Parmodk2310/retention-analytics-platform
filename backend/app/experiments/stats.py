import math
import numpy as np
from statsmodels.stats.proportion import proportions_ztest

def analyze_binary(control_conversions:int,control_n:int,treatment_conversions:int,treatment_n:int,alpha:float=0.05)->dict:
    if min(control_n,treatment_n)<=0: raise ValueError("both variants require observations")
    counts=np.array([treatment_conversions,control_conversions]);nobs=np.array([treatment_n,control_n])
    z,p=proportions_ztest(counts,nobs,alternative="two-sided")
    pc=control_conversions/control_n;pt=treatment_conversions/treatment_n;diff=pt-pc
    se=math.sqrt(pt*(1-pt)/treatment_n+pc*(1-pc)/control_n);zcrit=1.959963984540054
    return {"control_rate":pc,"treatment_rate":pt,"absolute_lift":diff,"relative_lift":diff/pc if pc else None,"z_stat":float(z),"p_value":float(p),"difference_ci":[diff-zcrit*se,diff+zcrit*se],"significant":bool(p<alpha),"alpha":alpha}
