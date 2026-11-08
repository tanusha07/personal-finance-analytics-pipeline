"""Shared database connection. Defaults match docker-compose.yml (local demo credentials)."""
import os

import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "expense_tracker"),
        user=os.getenv("DB_USER", "tracker"),
        password=os.getenv("DB_PASSWORD", "tracker_pass"),
    )
