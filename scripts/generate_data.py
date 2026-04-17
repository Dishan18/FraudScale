import json
import random
from datetime import datetime, timezone

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
    now = datetime.now(timezone.utc)
    if i % 20 == 0:
        user = "bot_user_1"
        base = "Great product"
        variations = [
            base,
            base + "!",
            "This is a great product",
            "Really great product",
            "Great product, works well"
        ]
        text = random.choice(variations)
    elif i % 25 == 0:
        user = f"burst_user_{random.randint(1,5)}"
        text = random.choice(reviews_text)
    else:
        user = random.choice(users)
        base = random.choice(reviews_text)

        variations = [
            base,
            base.lower(),
            f"I think this is {base.lower()}",
            f"{base}, would recommend",
            f"Not sure, but {base.lower()}",
        ]
        text = random.choice(variations)

    return {
        "user_id": user,
        "product_id": random.choice(products),
        "review_text": text,
        "rating": random.randint(1, 5),
        "timestamp": now.isoformat()
    }

def main():
    with open("data/reviews.json", "w") as f:
        for i in range(200000):
            review = generate_review(i)
            f.write(json.dumps(review) + "\n")

if __name__ == "__main__":
    main()