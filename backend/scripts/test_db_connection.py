"""
Quick MySQL connection test.
Run from project root: python backend/scripts/test_db_connection.py
"""
import os
import sys
from pathlib import Path

# Load .env from project root
root = Path(__file__).resolve().parent.parent.parent
env_path = root / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

host = os.getenv("DATABASE_HOST", "localhost")
port = int(os.getenv("DATABASE_PORT", "3306"))
user = os.getenv("DATABASE_USER", "root")
password = os.getenv("DATABASE_PASSWORD", "")
database = os.getenv("DATABASE_NAME", "sakoon")
use_sqlite = os.getenv("USE_SQLITE", "true").lower() == "true"

print("=== Sakoon AI - Database Connection Test ===\n")
print(f"USE_SQLITE: {use_sqlite}")
print(f"Host: {host}:{port}")
print(f"User: {user}")
print(f"Database: {database}")
print()

if use_sqlite:
    print("SQLite mode - skipping MySQL test.")
    sys.exit(0)

try:
    import mysql.connector
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchone()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("SUCCESS: MySQL connection OK!")
    print(f"Existing tables: {[t[0] for t in tables]}" if tables else "No tables yet (run init_sakoon.sql)")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)
