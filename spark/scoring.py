from pyspark.sql.functions import col, when, least, lit

def fraud_score(df):
    normalized_count = least(col("review_count") / 15.0, lit(1.0))
    normalized_rate = least(col("review_rate") / 2.0, lit(1.0))
    return df.withColumn(
        "fraud_score",
        (0.5 * col("similarity_score")) +
        (0.3 * normalized_rate) +
        (0.2 * normalized_count)
    )
def fraud_label(df):
    return df.withColumn(
        "is_fraud",
        when(col("fraud_score") >= 0.7, 1).otherwise(0)
    )
