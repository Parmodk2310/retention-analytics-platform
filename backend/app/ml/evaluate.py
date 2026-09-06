import numpy as np
from sklearn.metrics import average_precision_score,brier_score_loss,f1_score,precision_score,recall_score,roc_auc_score

def lift_at_k(y_true,prob,k:float=0.1)->float:
    y=np.asarray(y_true);p=np.asarray(prob);n=max(1,int(len(y)*k));top=y[np.argsort(-p)[:n]].mean();base=y.mean();return float(top/base) if base else 0.0

def evaluate_binary(y_true,prob,threshold:float=0.5)->dict:
    pred=(np.asarray(prob)>=threshold).astype(int)
    return {"roc_auc":float(roc_auc_score(y_true,prob)),"pr_auc":float(average_precision_score(y_true,prob)),"precision":float(precision_score(y_true,pred,zero_division=0)),"recall":float(recall_score(y_true,pred,zero_division=0)),"f1":float(f1_score(y_true,pred,zero_division=0)),"brier":float(brier_score_loss(y_true,prob)),"lift_at_10pct":lift_at_k(y_true,prob,0.1),"threshold":threshold}
