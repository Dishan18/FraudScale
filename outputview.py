import pandas as pd
import glob
import os

#to check parquet files in output/fraud and read them if they exist, then print the first few rows of the dataframes. This is a simple way to monitor the output of the streaming job without needing a full dashboard setup.

files = glob.glob("output/fraud/*.parquet")

valid_files = [f for f in files if os.path.getsize(f) > 0]

if not valid_files:
    print("No data files found yet.")
else:
    try:
        df = pd.concat([pd.read_parquet(f) for f in valid_files], ignore_index=True)
        if "window" in df.columns:
            df["window_start"] = df["window"].apply(
                lambda x: x.get("start") if isinstance(x, dict) else None
            )
            df["window_end"] = df["window"].apply(
                lambda x: x.get("end") if isinstance(x, dict) else None
            )

        if "window_start" in df.columns:
            df = df.sort_values("window_start")

        print(f"Loaded {len(df)} records:\n")

        columns_to_show = [
            col for col in [
                "window_start",
                "user_id",
                "review_count",
                "fraud_score",
                "is_fraud"
            ] if col in df.columns
        ]

        print(df[columns_to_show].head(20))

    except Exception as e:
        print(f"Error reading Parquet: {e}")