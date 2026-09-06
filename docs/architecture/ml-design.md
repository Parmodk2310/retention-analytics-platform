# Churn ML Design

The target is intentionally future-looking to prevent leakage. At snapshot date `T`, features use only `[T-90d, T)`. The label is `1` when no qualifying session or purchase occurs in `[T, T+30d)`. Validation is temporal rather than random. Logistic Regression is the baseline; XGBoost is a candidate. The selected model is based primarily on PR-AUC, with ROC-AUC, precision, recall, F1, Brier score and Lift@10% retained for business evaluation.

All categorical preprocessing is stored in the sklearn Pipeline, eliminating training/serving category-code skew. Production model artifacts may be stored in S3; web APIs read persisted scores instead of invoking training.
