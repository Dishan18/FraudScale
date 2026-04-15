import json
import random
import time
from datetime import datetime, timedelta, timezone

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
def generate_review(i):
    if i % 20 == 0:
        user = "bot_user_1"
        text = "Great product!"
    
    elif i % 15 == 0:
        user = random.choice(users)
        text = "Excellent item"
    
    elif i % 25 == 0:
        user = f"burst_user_{random.randint(1,5)}"
        text = random.choice(reviews_text)
    
    else:
        user = random.choice(users)
        text = random.choice(reviews_text)
    
    return {
        "user_id": user,
        "product_id": random.choice(products),
        "review_text": text,
        "rating": random.randint(1, 5),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
def main():
    with open("data/reviews.json", "w") as f:
        for i in range(200000):
            review = generate_review(i)
            f.write(json.dumps(review) + "\n")
if __name__ == "__main__":
    main()