#!/usr/bin/env python3
"""
MongoDB Users Database Setup
Database: users_mongo
Description: Base MongoDB con información de usuarios registrados
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB connection details (from datasources.yaml)
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_USER = "mongouser"
MONGO_PASSWORD = "mongopassword"
MONGO_DB = "users_db"
MONGO_COLLECTION = "users"

# Sample data
FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Eva", "Frank", "Grace", "Henry",
    "Iris", "Jack", "Karen", "Leo", "Mary", "Nathan", "Olivia", "Peter",
    "Quinn", "Rachel", "Steve", "Tina", "Uma", "Victor", "Wendy", "Xavier",
    "Yara", "Zack"
]

LAST_NAMES = [
    "Johnson", "Smith", "Williams", "Brown", "Martinez", "Garcia", "Lee",
    "Davis", "Rodriguez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore",
    "Jackson", "Martin", "Thompson", "White", "Lopez", "Gonzalez"
]

DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "company.com",
    "email.com", "mail.com", "example.com"
]


def generate_user(user_id):
    """Generate a fake user document"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(DOMAINS)}"

    # Random signup date in the last 2 years
    days_ago = random.randint(1, 730)
    signup_date = datetime.now() - timedelta(days=days_ago)

    return {
        "id": user_id,
        "name": name,
        "email": email,
        "signup_date": signup_date
    }


def main():
    """Main function to populate MongoDB"""
    print("=" * 60)
    print("MongoDB Users Database Setup")
    print("=" * 60)

    # Connect to MongoDB
    try:
        # Connection string with authentication
        connection_string = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
        client = MongoClient(connection_string)

        # Select database
        db = client[MONGO_DB]

        # Drop collection if exists (for clean re-runs)
        print(f"\nDropping collection '{MONGO_COLLECTION}' if it exists...")
        db[MONGO_COLLECTION].drop()

        # Get collection
        collection = db[MONGO_COLLECTION]

        # Generate and insert sample users
        print(f"\nInserting sample users into '{MONGO_COLLECTION}' collection...")
        users = [generate_user(i) for i in range(1, 26)]  # 25 users
        result = collection.insert_many(users)

        print(f"✓ Inserted {len(result.inserted_ids)} users successfully")

        # Create indexes for better query performance
        print("\nCreating indexes...")
        collection.create_index("id", unique=True)
        collection.create_index("email", unique=True)
        collection.create_index("signup_date")
        print("✓ Indexes created successfully")

        # Verify data
        print("\n" + "=" * 60)
        print("Data Verification")
        print("=" * 60)
        user_count = collection.count_documents({})
        print(f"Users count: {user_count}")

        # Show some sample documents
        print("\nSample users (first 5):")
        for user in collection.find().limit(5):
            print(f"  - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}, "
                  f"Signup: {user['signup_date'].strftime('%Y-%m-%d')}")

        # Show signup date range
        oldest = collection.find_one(sort=[("signup_date", 1)])
        newest = collection.find_one(sort=[("signup_date", -1)])
        if oldest and newest:
            print(f"\nSignup date range:")
            print(f"  Oldest: {oldest['signup_date'].strftime('%Y-%m-%d')}")
            print(f"  Newest: {newest['signup_date'].strftime('%Y-%m-%d')}")

        print("\n" + "=" * 60)
        print("✓ MongoDB population completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    finally:
        if 'client' in locals():
            client.close()

    return 0


if __name__ == "__main__":
    exit(main())
