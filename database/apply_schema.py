#!/usr/bin/env python3
"""
Apply database schema to PostgreSQL.

Usage:
    python database/apply_schema.py           # Safe mode - preserves data
    python database/apply_schema.py --fresh   # Fresh start - deletes all data
"""

import os
import sys
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_url():
    """Get database URL from environment or use default."""
    return os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:crapcrap@localhost:5432/content_analysis'
    )


def apply_schema(fresh=False):
    """
    Apply database schema.

    Args:
        fresh: If True, drops all tables first (DESTRUCTIVE)
    """
    # Choose which SQL file to use
    if fresh:
        schema_path = Path(__file__).parent / 'schema_fresh.sql'
        print("⚠️  WARNING: Running in FRESH mode - ALL DATA WILL BE DELETED!")
        print("This will drop all tables and recreate them.")
        response = input("Are you sure? Type 'yes' to continue: ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    else:
        schema_path = Path(__file__).parent / 'schema.sql'
        print("Running in SAFE mode - will only create tables if they don't exist")

    # Read the SQL file
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Connect to database
    database_url = get_database_url()
    print(f"\nConnecting to database...")

    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        # Execute the schema
        print("Applying schema...")
        cursor.execute(schema_sql)
        print("✅ Schema applied successfully!")

        # Show tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print("\n📊 Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")

        # Show row counts
        print("\n📈 Row counts:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")

    except Exception as e:
        print(f"\n❌ Error applying schema: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    # Check for --fresh flag
    fresh = '--fresh' in sys.argv
    apply_schema(fresh=fresh)