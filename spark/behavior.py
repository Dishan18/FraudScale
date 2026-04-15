from pyspark.sql.functions import col, to_timestamp, window, count, first, to_timestamp
def add_timestamp(df):
    return df.withColumn(
        "timestamp",
        to_timestamp(col("timestamp"))
    )

def behavioral_features(df):
    df = df.withWatermark("timestamp", "1 minute")

    return df.groupBy(
        window(col("timestamp"), "2 minutes"),
        col("user_id")
    ).agg(
        count("*").alias("review_count"),
        first("review_text").alias("sample_text")
    )