from pyspark.sql.functions import col, to_timestamp, window, count

def add_timestamp(df):
    return df.withColumn(
        "timestamp",
        to_timestamp(col("timestamp"))
    )

def behavioral_features(df):
    df = df.withWatermark("timestamp", "5 minutes")

    return df.groupBy(
        window(col("timestamp"), "2 minutes"),
        col("user_id")
    ).agg(
        count("*").alias("review_count")
    )