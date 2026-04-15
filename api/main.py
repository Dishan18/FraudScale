from fastapi import FastAPI, Query
import pandas as pd
import os
import time

app = FastAPI()

_cached_df = None
_last_load_time = 0
CACHE_TTL = 10  

DATA_PATH = "output/fraud"

def load_data():
    global _cached_df, _last_load_time

    current_time = time.time()

    if _cached_df is None or (current_time - _last_load_time > CACHE_TTL):
        if not os.path.exists(DATA_PATH):
            return pd.DataFrame()

        try:
            _cached_df = pd.read_parquet(DATA_PATH)
            _last_load_time = current_time
        except Exception as e:
            print("Parquet read error:", e)
            return _cached_df if _cached_df is not None else pd.DataFrame()

    return _cached_df

@app.get("/")
def home():
    return {"message": "FraudScale API running"}

@app.get("/fraud")
def get_fraud(limit: int = 50):
    df = load_data()
    if df.empty:
        return []

    return df.tail(limit).to_dict(orient="records")

@app.get("/fraud/flagged")
def get_flagged(limit: int = 50):
    df = load_data()
    if df.empty:
        return []

    df = df[df["is_fraud"] == 1]
    return df.tail(limit).to_dict(orient="records")

@app.get("/user/{user_id}")
def get_user(user_id: str):
    df = load_data()
    if df.empty:
        return []

    df = df[df["user_id"] == user_id]
    return df.to_dict(orient="records")

@app.get("/stats")
def stats():
    df = load_data()
    if df.empty:
        return {}

    return {
        "total_records": len(df),
        "fraud_count": int((df["is_fraud"] == 1).sum()),
        "unique_users": df["user_id"].nunique()
    }