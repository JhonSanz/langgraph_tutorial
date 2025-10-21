#!/usr/bin/env python3
"""
MongoDB System Logs Database Setup
Database: system_logs_db
Description: Base MongoDB con logs del sistema, eventos, errores y métricas
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB connection details (from datasources.yaml)
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_USER = "mongouser"
MONGO_PASSWORD = "mongopassword"
MONGO_DB = "system_logs_db"
MONGO_COLLECTION = "logs"

# Sample data for log generation
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG_LEVEL_WEIGHTS = [10, 50, 20, 15, 5]  # More INFO logs, fewer CRITICAL

SERVICES = [
    "auth-service",
    "payment-gateway",
    "user-api",
    "notification-service",
    "analytics-engine",
    "file-storage",
    "email-sender",
    "cache-manager",
    "database-connector",
    "api-gateway"
]

# Log messages templates by level
LOG_MESSAGES = {
    "DEBUG": [
        "Cache hit for key: user_{user_id}",
        "Query execution time: {duration_ms}ms",
        "Request received from {ip_address}",
        "Session initialized for user {user_id}",
        "Connection pool status: active={user_id}/100"
    ],
    "INFO": [
        "User {user_id} logged in successfully",
        "Payment processed: ${amount}",
        "Email sent to user {user_id}",
        "File uploaded: {filename}",
        "API request completed: {endpoint}",
        "Report generated for period {period}",
        "Background job completed: {job_name}",
        "Configuration reloaded"
    ],
    "WARNING": [
        "High memory usage: {percentage}%",
        "Slow query detected: {duration_ms}ms",
        "API rate limit approaching for IP {ip_address}",
        "Cache miss ratio high: {percentage}%",
        "Connection pool nearly exhausted",
        "Deprecated API endpoint accessed: {endpoint}"
    ],
    "ERROR": [
        "Database connection failed: timeout after {duration_ms}ms",
        "Payment gateway error: transaction declined",
        "Failed to send email to user {user_id}",
        "File upload failed: size exceeds limit",
        "Authentication failed for user {user_id}",
        "API request failed with status {status_code}",
        "External service unavailable: {service}"
    ],
    "CRITICAL": [
        "Database connection pool exhausted",
        "Out of memory: emergency restart required",
        "Security breach detected from IP {ip_address}",
        "Payment processing service crashed",
        "Data corruption detected in table {table_name}",
        "Multiple authentication failures: possible attack"
    ]
}

HTTP_STATUS_CODES = [200, 201, 204, 400, 401, 403, 404, 500, 502, 503]
IP_ADDRESSES = [
    "192.168.1.100", "192.168.1.101", "192.168.1.102",
    "10.0.0.50", "10.0.0.51", "10.0.0.52",
    "172.16.0.10", "172.16.0.11", "172.16.0.12"
]


def generate_log(index):
    """Generate a fake system log entry"""
    # Random timestamp in the last 30 days
    minutes_ago = random.randint(1, 43200)  # 30 days in minutes
    timestamp = datetime.now() - timedelta(minutes=minutes_ago)

    # Weighted random level (more INFO, less CRITICAL)
    level = random.choices(LOG_LEVELS, weights=LOG_LEVEL_WEIGHTS, k=1)[0]

    # Random service
    service = random.choice(SERVICES)

    # Generate message based on level
    message_template = random.choice(LOG_MESSAGES[level])
    message = message_template.format(
        user_id=random.randint(1, 1000),
        duration_ms=random.randint(10, 5000),
        ip_address=random.choice(IP_ADDRESSES),
        amount=random.randint(10, 1000),
        filename=f"file_{random.randint(1, 100)}.pdf",
        endpoint=f"/api/v1/{random.choice(['users', 'products', 'orders', 'reports'])}",
        period="2025-Q1",
        job_name=f"job_{random.randint(1, 20)}",
        percentage=random.randint(70, 99),
        service=random.choice(SERVICES),
        status_code=random.choice(HTTP_STATUS_CODES),
        table_name=f"table_{random.randint(1, 10)}"
    )

    log_entry = {
        "timestamp": timestamp,
        "level": level,
        "service": service,
        "message": message,
        "request_id": f"req_{index}_{random.randint(1000, 9999)}"
    }

    # Add optional fields based on log type
    if random.random() > 0.3:  # 70% of logs have user_id
        log_entry["user_id"] = random.randint(1, 1000)

    if "ms" in message or random.random() > 0.5:
        log_entry["duration_ms"] = random.randint(10, 5000)

    if level in ["ERROR", "CRITICAL"] or random.random() > 0.4:
        log_entry["status_code"] = random.choice(HTTP_STATUS_CODES)

    if random.random() > 0.4:  # 60% of logs have IP
        log_entry["ip_address"] = random.choice(IP_ADDRESSES)

    return log_entry


def main():
    """Main function to populate MongoDB with system logs"""
    print("=" * 60)
    print("MongoDB System Logs Database Setup")
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

        # Generate and insert sample logs (500 logs)
        print(f"\nGenerating and inserting system logs into '{MONGO_COLLECTION}' collection...")
        logs = [generate_log(i) for i in range(1, 501)]
        result = collection.insert_many(logs)

        print(f"✓ Inserted {len(result.inserted_ids)} log entries successfully")

        # Create indexes for better query performance
        print("\nCreating indexes...")
        collection.create_index("timestamp")
        collection.create_index("level")
        collection.create_index("service")
        collection.create_index("user_id")
        collection.create_index([("timestamp", -1), ("level", 1)])  # Compound index
        print("✓ Indexes created successfully")

        # Verify data
        print("\n" + "=" * 60)
        print("Data Verification")
        print("=" * 60)

        log_count = collection.count_documents({})
        print(f"Total logs: {log_count}")

        # Show log distribution by level
        print("\nLogs by level:")
        for level in LOG_LEVELS:
            count = collection.count_documents({"level": level})
            print(f"  - {level}: {count} logs")

        # Show recent errors
        print("\nRecent ERROR and CRITICAL logs (last 5):")
        recent_errors = collection.find(
            {"level": {"$in": ["ERROR", "CRITICAL"]}}
        ).sort("timestamp", -1).limit(5)

        for log in recent_errors:
            print(f"  - [{log['timestamp'].strftime('%Y-%m-%d %H:%M')}] {log['level']} - {log['service']}: {log['message'][:60]}...")

        # Show service statistics
        print("\nLogs by service (top 5):")
        pipeline = [
            {"$group": {"_id": "$service", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        for result in collection.aggregate(pipeline):
            print(f"  - {result['_id']}: {result['count']} logs")

        # Time range
        oldest = collection.find_one(sort=[("timestamp", 1)])
        newest = collection.find_one(sort=[("timestamp", -1)])
        if oldest and newest:
            print(f"\nTime range:")
            print(f"  Oldest log: {oldest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Newest log: {newest['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        print("\n" + "=" * 60)
        print("✓ MongoDB logs population completed successfully!")
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
