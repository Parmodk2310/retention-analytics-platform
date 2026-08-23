import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support

def train_churn_model(df: pd.DataFrame):
    # Label: no activity in 30 days
    X = df.drop(['user_id', 'churned', 'last_session_date'], axis=1)
    y = df['churned']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    models = {
        'logistic_regression': Pipeline([
            ('features', RFMFeatureEngineer()),
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(class_weight='balanced', max_iter=1000))
        ]),
        'random_forest': Pipeline([
            ('features', RFMFeatureEngineer()),
            ('clf', RandomForestClassifier(n_estimators=200, class_weight='balanced'))
        ]),
        'xgboost': Pipeline([
            ('features', RFMFeatureEngineer()),
            ('clf', xgb.XGBClassifier(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.05,
                scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1]),
                eval_metric='auc',
                use_label_encoder=False
            ))
        ])
    }
    
    results = {}
    best_model, best_auc = None, 0
    
    for name, pipeline in models.items():
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring='roc_auc')
        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        auc = roc_auc_score(y_test, y_prob)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
        
        results[name] = {
            'cv_auc_mean': cv_scores.mean(),
            'cv_auc_std': cv_scores.std(),
            'test_auc': auc,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        if auc > best_auc:
            best_auc = auc
            best_model = pipeline
    
    joblib.dump(best_model, 'app/ml/artifacts/churn_xgb_v1.joblib')
    return results, best_model