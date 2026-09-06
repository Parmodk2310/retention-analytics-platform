import numpy as np
STAGE_BASE={"search":.78,"add_to_cart":.52,"checkout":.67,"purchase":.76}

def session_events(rng:np.random.Generator,engagement:float,variant:str,is_first_14d:bool)->list[str]:
    stages=["session_start","page_view"]
    if rng.random()>min(.97,STAGE_BASE["search"]*(.65+.55*engagement)):return stages+["session_end"]
    stages.append("search")
    cart_p=STAGE_BASE["add_to_cart"]*(.58+.62*engagement)
    # Treatment effect is applied only in the activation window; ~12% relative uplift in cart progression.
    if variant=="treatment" and is_first_14d:cart_p*=1.12
    if rng.random()>min(.95,cart_p):return stages+["session_end"]
    stages.append("add_to_cart")
    if rng.random()>min(.94,STAGE_BASE["checkout"]*(.72+.38*engagement)):return stages+["session_end"]
    stages.append("checkout")
    if rng.random()>min(.93,STAGE_BASE["purchase"]*(.70+.38*engagement)):return stages+["session_end"]
    stages.append("purchase");stages.append("session_end");return stages
