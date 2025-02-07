# File: app/utils/anomaly_detection.py
import pandas as pd
import numpy as np
import json
from datetime import datetime
from app.services.db_manager import get_connection
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder

def load_events():

    try:
        with get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM events", conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        return df
    except Exception as e:
        print("Error loading events:", e)
        return pd.DataFrame()

def preprocess_events(df):

    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    df['timestamp_numeric'] = df['timestamp'].apply(lambda x: x.timestamp() if pd.notnull(x) else 0)
    
    features = df[['event_category', 'event_type', 'timestamp_numeric']].fillna("Unknown")
    
    from sklearn.preprocessing import OneHotEncoder
    encoder = OneHotEncoder(sparse=False)
    categorical_data = features[['event_category', 'event_type']]
    onehot = encoder.fit_transform(categorical_data)
    
    import numpy as np
    X = np.hstack([onehot, features[['timestamp_numeric']].values])
    return X, encoder


def detect_anomalies(df):

    if df.empty:
        return df

    X, encoder = preprocess_events(df)
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    df['anomaly'] = model.predict(X)
    return df

def get_anomaly_summary(df):

    if df.empty:
        return pd.DataFrame()
    summary = df.groupby('device_id').agg(
        total_events=('id', 'count'),
        anomalies=('anomaly', lambda x: (x == -1).sum())
    ).reset_index()
    summary['anomaly_ratio'] = summary['anomalies'] / summary['total_events']
    return summary
