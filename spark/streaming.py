from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, IntegerType
from spark.heuristics import apply_heuristics
from spark.behavior import add_timestamp, behavioral_features

def create_spark_session():
    spark = SparkSession.builder \
        .appName("FraudScale") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.sql.adaptive.enabled", "true") \
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
        .option("maxOffsetsPerTrigger", 5000) \
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
        .format("console") \
        .outputMode("update") \
        .trigger(processingTime="3 seconds") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    spark = create_spark_session()
    kafka_df = read_kafka_stream(spark)
    parsed_df = parse_stream(kafka_df)
    filtered_df = apply_heuristics(parsed_df)
    timestamped_df = add_timestamp(filtered_df)
    behavior_df = behavioral_features(timestamped_df)

    start_stream(behavior_df)    