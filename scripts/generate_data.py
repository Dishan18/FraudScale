import json
import random
import time
from datetime import datetime, timedelta

users = [f"user_{i}" for i in range(1000)]
products = [f"product_{i}" for i in range(500)]

reviews_text = [
    "Great product!",
    "Very bad quality",
    "Worth the price",
    "Terrible experience",
    "Excellent item",
    "Not as expected",
    "Loved it",
    "Horrible",
    "Average product",
]
def generate_review():
    return {
        "user_id": random.choice(users),
        "product_id": random.choice(products),
        "review_text": random.choice(reviews_text),
        "rating": random.randint(1, 5),
        "timestamp": (datetime.utcnow() - timedelta(seconds=random.randint(0, 300))).isoformat()
    }
def main():
    with open("data/reviews.json", "w") as f:
        for _ in range(200000):
            review = generate_review()
            f.write(json.dumps(review) + "\n")
if __name__ == "__main__":
    main()