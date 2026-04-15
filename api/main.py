from fastapi import FastAPI
import pandas as pd
import os
import time
import glob
import numpy as np
import json

app = FastAPI()

# -----------------------
# PATH CONFIG
# -----------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(BASE_DIR, "output", "fraud")
LIVE_PATH = os.path.join(BASE_DIR, "output", "live")

CACHE_TTL = 10
_cached_df = None
_last_load_time = 0


# -----------------------
# SAFE JSON CONVERSION (FINAL FIX)
# -----------------------
def clean_value(v):
    import math

    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
        return float(v)

    if isinstance(v, (list, tuple)):
        return [clean_value(x) for x in v]

    if isinstance(v, dict):
        return {k: clean_value(val) for k, val in v.items()}

    return v


def safe_json(data):
    if isinstance(data, list):
        return [clean_value(item) for item in data]
    if isinstance(data, dict):
        return clean_value(data)
    return data


# -----------------------
# LOAD PARQUET
# -----------------------
def load_data():
    global _cached_df, _last_load_time

    current_time = time.time()

    if _cached_df is None or (current_time - _last_load_time > CACHE_TTL):

        files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
        valid_files = [f for f in files if os.path.exists(f) and os.path.getsize(f) > 0]

        if not valid_files:
            return _cached_df if _cached_df is not None else pd.DataFrame()

        try:
            _cached_df = pd.concat(
                [pd.read_parquet(f) for f in valid_files],
                ignore_index=True
            )
            _last_load_time = current_time
        except Exception as e:
            print("Parquet read error:", e)
            return _cached_df if _cached_df is not None else pd.DataFrame()

    return _cached_df


# -----------------------
# LOAD LIVE JSON
# -----------------------
def load_live_data():
    files = glob.glob(os.path.join(LIVE_PATH, "part-*.json"))

    if not files:
        return pd.DataFrame()

    dfs = []

    for f in files:
        try:
            df = pd.read_json(f, lines=True, dtype=False)
            dfs.append(df)
        except Exception as e:
            print("Live read error:", f, e)

    if not dfs:
        return pd.DataFrame()

    return pd.concat(dfs, ignore_index=True)


# -----------------------
# ROOT
# -----------------------
@app.get("/")
def home():
    return {"message": "FraudScale API running"}


# -----------------------
# LIVE
# -----------------------
@app.get("/live")
def get_live():
    df = load_live_data()

    if df.empty:
        df = load_data()

    if df.empty:
        return []

    # drop heavy/nested column
    if "embedding" in df.columns:
        df = df.drop(columns=["embedding"])

    # sort for dashboard
    if "review_count" in df.columns:
        df = df.sort_values("review_count", ascending=False)

    data = df.to_dict(orient="records")

    return safe_json(data)


# -----------------------
# STATS
# -----------------------
@app.get("/stats")
def stats():
    df = load_live_data()

    if df.empty:
        df = load_data()

    if df.empty:
        return {}

    total = len(df)
    fraud = int(df["is_fraud"].sum())

    result = {
        "total_records": int(total),
        "fraud_count": int(fraud),
        "fraud_rate": float(fraud / total) if total > 0 else 0.0,
        "unique_users": int(df["user_id"].nunique())
    }

    return safe_json(result)


# -----------------------
# FRAUD LOGS
# -----------------------
@app.get("/fraud/logs")
def fraud_logs(limit: int = 50):
    df = load_data()

    if df.empty:
        return []

    if "window" in df.columns:
        df["window_start"] = df["window"].apply(
            lambda x: x["start"] if isinstance(x, dict) else None
        )
        df = df.sort_values("window_start", ascending=False)

    if "embedding" in df.columns:
        df = df.drop(columns=["embedding"])

    data = df.head(limit).to_dict(orient="records")

    return safe_json(data)


# -----------------------
# FLAGGED USERS
# -----------------------
@app.get("/fraud/flagged")
def get_flagged(limit: int = 50):
    df = load_data()

    if df.empty:
        return []

    df = df[df["is_fraud"] == 1]["user_id"].nunique()

    data = df.tail(limit).to_dict(orient="records")

    return safe_json(data)


# -----------------------
# USER
# -----------------------
@app.get("/user/{user_id}")
def get_user(user_id: str):
    df = load_data()

    if df.empty:
        return []

    df = df[df["user_id"] == user_id]

    data = df.to_dict(orient="records")

    return safe_json(data)