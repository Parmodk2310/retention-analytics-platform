import numpy as np

def transformed_feature_importance(pipeline)->list[dict]:
    pre=pipeline.named_steps["preprocess"];model=pipeline.named_steps["model"]
    names=pre.get_feature_names_out();values=getattr(model,"feature_importances_",None)
    if values is None:return []
    order=np.argsort(-values)[:20]
    return [{"feature":str(names[i]),"importance":float(values[i])} for i in order]
