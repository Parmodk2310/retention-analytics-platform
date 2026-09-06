import numpy as np
def purchase_amount(rng:np.random.Generator)->float:
    return float(round(np.clip(rng.lognormal(mean=3.35,sigma=.65),5,600),2))
