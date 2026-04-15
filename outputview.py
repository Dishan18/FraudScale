import pandas as pd
import glob
import os

# 1. Find all parquet files
files = glob.glob("output/fraud/*.parquet")

# 2. Keep only non-empty files
valid_files = [f for f in files if os.path.getsize(f) > 0]

if not valid_files:
    print("⚠️ No data files found yet.")
else:
    try:
        # 3. Read all parquet files
        df = pd.concat([pd.read_parquet(f) for f in valid_files], ignore_index=True)

        # 4. Extract window fields safely
        if "window" in df.columns:
            df["window_start"] = df["window"].apply(
                lambda x: x.get("start") if isinstance(x, dict) else None
            )
            df["window_end"] = df["window"].apply(
                lambda x: x.get("end") if isinstance(x, dict) else None
            )

        # 5. Sort by window_start (safe)
        if "window_start" in df.columns:
            df = df.sort_values("window_start")

        # 6. Display clean output
        print(f"✅ Loaded {len(df)} records:\n")

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
        print(f"❌ Error reading Parquet: {e}")