from pyspark.sql.functions import col, to_timestamp, window, count, first, to_timestamp
def add_timestamp(df):
    return df.withColumn(
        "timestamp",
        to_timestamp(col("timestamp"))
    )

def behavioral_features(df):
    df = df.withWatermark("timestamp", "10 seconds")

    return df.groupBy(
        window(col("timestamp"), "30 seconds"),
        col("user_id")
    ).agg(
        count("*").alias("review_count"),
        (count("*") / 30.0).alias("review_rate"),
        first("review_text").alias("sample_text")
    )