import numpy as np
def cuped_adjust(outcome:np.ndarray,covariate:np.ndarray)->np.ndarray:
    variance=np.var(covariate,ddof=1)
    if variance==0:return outcome.copy()
    theta=np.cov(outcome,covariate,ddof=1)[0,1]/variance
    return outcome-theta*(covariate-np.mean(covariate))
