from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from spark.heuristics import apply_heuristics
from spark.behavior import add_timestamp, behavioral_features
from spark.scoring import fraud_score, fraud_label
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, FloatType, TimestampType
from spark.ai_service import generate_embeddings

def create_spark_session():
    spark = SparkSession.builder \
        .appName("FraudScale") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "1") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.python.worker.reuse", "true") \
        .config("spark.executor.instances", "1") \
        .config("spark.executor.cores", "2") \
        .config("spark.sql.adaptive.shuffle.targetPostShuffleInputSize", "64MB") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.streaming.backpressure.enabled", "true") \
        .getOrCreate()

    return spark
def read_kafka_stream(spark):
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "reviews") \
        .option("startingOffsets", "latest") \
        .option("maxOffsetsPerTrigger", 1000) \
        .load()
    return df
def parse_stream(df):
    schema = StructType() \
        .add("user_id", StringType()) \
        .add("product_id", StringType()) \
        .add("review_text", StringType()) \
        .add("rating", IntegerType()) \
        .add("timestamp", StringType())

    parsed = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    return parsed
def start_stream(df):
    query = df.writeStream \
        .format("parquet") \
        .option("path", "output/fraud") \
        .option("checkpointLocation", "output/checkpoints") \
        .outputMode("append") \
        .trigger(processingTime="15 seconds") \
        .start()

    query.awaitTermination()

schema = StructType([
    StructField("window", StructType([
        StructField("start", TimestampType()),
        StructField("end", TimestampType())
    ])),
    StructField("user_id", StringType()),
    StructField("review_count", IntegerType()),
    StructField("sample_text", StringType()),
    StructField("embedding", ArrayType(FloatType())),
    StructField("is_similar", IntegerType())
])

if __name__ == "__main__":
    spark = create_spark_session()
    kafka_df = read_kafka_stream(spark)
    parsed_df = parse_stream(kafka_df)
    filtered_df = apply_heuristics(parsed_df)
    timestamped_df = add_timestamp(filtered_df)
    behavior_df = behavioral_features(timestamped_df)
    ai_df = behavior_df.mapInPandas(generate_embeddings, schema=schema)
    scored_df = fraud_score(ai_df)
    final_df = fraud_label(scored_df)

    start_stream(final_df)