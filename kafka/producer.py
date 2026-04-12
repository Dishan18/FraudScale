import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    linger_ms=5,      
    batch_size=32768,   
    acks=1
)

def stream_data():
    print("Starting stream to Kafka topic 'reviews'...")
    count = 0
    try:
        with open("data/reviews.json", "r") as f:
            for line in f:
                review = json.loads(line)
                producer.send("reviews", review)
                
                count += 1
                if count % 5000 == 0:
                    print(f"Sent {count} reviews...")

                time.sleep(0.001) 
                
    except FileNotFoundError:
        print("Error: data/reviews.json not found. Run generate_data.py first!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.flush()
        print(f"Streaming complete. Total sent: {count}")

if __name__ == "__main__":
    stream_data()