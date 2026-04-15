from pyspark.sql.functions import col, when

def fraud_score(df):
    return df.withColumn(
        "fraud_score",
        when(
            (col("review_count") >= 10) | (col("is_similar") == 1),
            1.0
        )
        .when(col("review_count") >= 5, 0.4)
        .otherwise(0.0)
    )
def fraud_label(df):
    return df.withColumn(
        "is_fraud",
        when(col("fraud_score") >= 0.7, 1).otherwise(0)
    )