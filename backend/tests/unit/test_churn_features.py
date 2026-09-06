from app.ml.labels import churn_label
def test_future_label(): assert churn_label(0)==1 and churn_label(1)==0
