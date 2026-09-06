from prometheus_client import Counter, Histogram
HTTP_REQUESTS=Counter("http_requests_total","HTTP requests",["method","path","status"])
HTTP_REQUEST_DURATION=Histogram("http_request_duration_seconds","HTTP request duration",["method","path"])
ANALYTICS_QUERY_DURATION=Histogram("analytics_query_duration_seconds","Analytics query duration",["query"])
EXPERIMENT_EXPOSURES=Counter("experiment_exposures_total","Experiment exposures",["experiment","variant"])
CHURN_PREDICTIONS=Counter("churn_predictions_total","Persisted churn predictions",["risk_band"])
