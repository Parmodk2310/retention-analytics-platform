import math
import numpy as np
BASE_RETENTION={"organic":.965,"referral":.960,"email":.950,"affiliate":.942,"paid_social":.925}
def active_probability(channel:str,engagement:float,days_since_signup:int)->float:
    weekly=max(0,days_since_signup/7);decay=BASE_RETENTION[channel]**weekly
    return float(np.clip((.15+.85*engagement)*decay,.015,.95))
def sessions_for_active_day(rng:np.random.Generator,engagement:float,weekend:bool)->int:
    lam=.8+2.1*engagement+(0.35 if weekend else 0);return max(1,int(rng.poisson(lam)))
