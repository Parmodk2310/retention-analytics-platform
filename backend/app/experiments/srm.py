from scipy.stats import chisquare
def sample_ratio_mismatch(observed:dict[str,int],allocation:dict[str,float],alpha:float=0.01)->dict:
    total=sum(observed.values());keys=list(allocation)
    obs=[observed.get(k,0) for k in keys];expected=[total*allocation[k] for k in keys]
    if total==0:return {"p_value":1.0,"detected":False,"observed":observed,"expected":dict(zip(keys,expected,strict=True))}
    stat,p=chisquare(obs,f_exp=expected)
    return {"chi_square":float(stat),"p_value":float(p),"detected":bool(p<alpha),"observed":observed,"expected":dict(zip(keys,[round(x,2) for x in expected],strict=True))}
