# File: app/utils/anomaly_detection.py
import pandas as pd
from sklearn.ensemble import IsolationForest
import json
from app.services.database.db_manager import get_connection

def load_events():

    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM events", conn)
    return df

def detect_anomalies(df, contamination=0.1):

    df = df.copy()
    df['timestamp_numeric'] = pd.to_datetime(df['timestamp'], errors='coerce').astype('int64') // 10**9
    clf = IsolationForest(contamination=contamination, random_state=42)
    df['anomaly'] = clf.fit_predict(df[['timestamp_numeric']])
    df['anomaly_score'] = clf.decision_function(df[['timestamp_numeric']])
    return df

def get_anomaly_summary(df):

    anomalies = df[df['anomaly'] == -1]
    summary = anomalies.groupby('device_id').size().reset_index(name='anomaly_count')
    return summary
