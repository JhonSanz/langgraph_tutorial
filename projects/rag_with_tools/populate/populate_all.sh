#!/bin/bash
# Script to populate all databases with fake data
# Ensures all database containers are running before executing

set -e  # Exit on error

echo "======================================"
echo "Database Population Script"
echo "======================================"
echo ""

# Check if all database containers are running
echo "Checking database containers..."
MISSING_CONTAINERS=()

if ! docker ps | grep -q postgres_db; then
    MISSING_CONTAINERS+=("postgres_db")
fi

if ! docker ps | grep -q mysql_db; then
    MISSING_CONTAINERS+=("mysql_db")
fi

if ! docker ps | grep -q mongo_db; then
    MISSING_CONTAINERS+=("mongo_db")
fi

if [ ${#MISSING_CONTAINERS[@]} -ne 0 ]; then
    echo "Error: The following containers are not running:"
    for container in "${MISSING_CONTAINERS[@]}"; do
        echo "  - $container"
    done
    echo ""
    echo "Please start them with: docker-compose up -d"
    exit 1
fi

echo "✓ All database containers are running"
echo ""

# Check and install required Python packages
echo "Checking Python dependencies..."
PACKAGES_TO_INSTALL=()

if ! python3 -c "import sqlalchemy" 2>/dev/null; then
    PACKAGES_TO_INSTALL+=("sqlalchemy")
fi

if ! python3 -c "import mysql.connector" 2>/dev/null; then
    PACKAGES_TO_INSTALL+=("mysql-connector-python")
fi

if ! python3 -c "import pymongo" 2>/dev/null; then
    PACKAGES_TO_INSTALL+=("pymongo")
fi

if [ ${#PACKAGES_TO_INSTALL[@]} -ne 0 ]; then
    echo "Installing missing packages: ${PACKAGES_TO_INSTALL[*]}"
    pip3 install "${PACKAGES_TO_INSTALL[@]}"
    echo ""
fi

echo "✓ All Python dependencies are satisfied"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Track overall success
OVERALL_SUCCESS=0

# Execute PostgreSQL population script
echo "======================================"
echo "1. Populating PostgreSQL (sales_db)"
echo "======================================"
if python3 "${SCRIPT_DIR}/postgres_sales.py"; then
    echo "✓ PostgreSQL population completed"
else
    echo "✗ PostgreSQL population failed"
    OVERALL_SUCCESS=1
fi
echo ""

# Execute MySQL population script
echo "======================================"
echo "2. Populating MySQL (human_resources_db)"
echo "======================================"
if python3 "${SCRIPT_DIR}/mysql_hr.py"; then
    echo "✓ MySQL population completed"
else
    echo "✗ MySQL population failed"
    OVERALL_SUCCESS=1
fi
echo ""

# Execute MongoDB population script
echo "======================================"
echo "3. Populating MongoDB (system_logs)"
echo "======================================"
if python3 "${SCRIPT_DIR}/mongo_logs.py"; then
    echo "✓ MongoDB population completed"
else
    echo "✗ MongoDB population failed"
    OVERALL_SUCCESS=1
fi
echo ""

# Final summary
echo "======================================"
if [ $OVERALL_SUCCESS -eq 0 ]; then
    echo "✓ All databases populated successfully!"
else
    echo "✗ Some databases failed to populate"
fi
echo "======================================"

exit $OVERALL_SUCCESS
