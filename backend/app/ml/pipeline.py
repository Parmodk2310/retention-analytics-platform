from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from app.ml.features import CATEGORICAL_FEATURES,NUMERIC_FEATURES

def preprocessor()->ColumnTransformer:
    numeric=Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    categorical=Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore",sparse_output=True))])
    return ColumnTransformer([("num",numeric,NUMERIC_FEATURES),("cat",categorical,CATEGORICAL_FEATURES)])
def logistic_pipeline()->Pipeline:
    return Pipeline([("preprocess",preprocessor()),("model",LogisticRegression(max_iter=1500,class_weight="balanced",C=1.0))])
def xgboost_pipeline(scale_pos_weight:float=1.0)->Pipeline:
    return Pipeline([("preprocess",preprocessor()),("model",xgb.XGBClassifier(n_estimators=350,max_depth=5,learning_rate=0.04,subsample=0.85,colsample_bytree=0.85,reg_lambda=2.0,min_child_weight=3,scale_pos_weight=scale_pos_weight,eval_metric="aucpr",random_state=42,n_jobs=-1))])
