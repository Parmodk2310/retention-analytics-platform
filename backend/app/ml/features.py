import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class RFMFeatureEngineer(BaseEstimator, TransformerMixin):
    """Recency, Frequency, Monetary + Engagement features"""
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        now = pd.Timestamp.now()
        features = pd.DataFrame()
        
        # Recency
        features['days_since_last_login'] = (now - X['last_session_date']).dt.days
        
        # Frequency
        features['session_count_30d'] = X['session_count_30d']
        features['session_count_90d'] = X['session_count_90d']
        features['avg_sessions_per_week'] = X['session_count_90d'] / 13
        
        # Monetary
        features['total_revenue'] = X['total_revenue']
        features['avg_order_value'] = X['total_revenue'] / X['order_count'].clip(lower=1)
        
        # Engagement depth
        features['avg_session_duration'] = X['avg_session_duration']
        features['search_count_30d'] = X['search_count_30d']
        features['cart_abandon_rate'] = 1 - (X['checkout_count'] / X['cart_add_count'].clip(lower=1))
        
        # Categorical encoding
        features['is_mobile'] = (X['device_type'] != 'web').astype(int)
        features['channel_encoded'] = X['acquisition_channel'].astype('category').cat.codes
        
        return features.fillna(0)