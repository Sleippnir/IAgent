import sqlite3
import os
from loguru import logger

def get_db_connection():
    database_url = os.getenv("DATABASE_URL", "interview_data.db")
    conn = sqlite3.connect(database_url)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop tables if they exist for a clean setup
    cursor.execute("DROP TABLE IF EXISTS roles")
    cursor.execute("DROP TABLE IF EXISTS questions")

    # Create roles table
    cursor.execute("""
        CREATE TABLE roles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            seniority TEXT,
            jd_text TEXT
        )
    """)

    # Create questions table
    cursor.execute("""
        CREATE TABLE questions (
            id TEXT PRIMARY KEY,
            role_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            ideal_answer_text TEXT,
            order_index INTEGER,
            FOREIGN KEY (role_id) REFERENCES roles (id)
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Database tables created successfully.")

import json
import hashlib

def load_mock_data(conn):
    with open("test_data/mock_data.json", "r") as f:
        data = json.load(f)
    cursor = conn.cursor()

    for role in data["roles"]:
        role_id = role["job_description"]["id"]
        cursor.execute(
            "INSERT INTO roles (id, title, seniority, jd_text) VALUES (?, ?, ?, ?)",
            (role_id, role["role_title"], role["seniority_level"], role["job_description"]["text"])
        )
        for i, item in enumerate(role["interview"]):
            cursor.execute(
                "INSERT INTO questions (id, role_id, question_text, ideal_answer_text, order_index) VALUES (?, ?, ?, ?, ?)",
                (item["question"]["id"], role_id, item["question"]["text"], item["ideal_answer"]["text"], i)
            )

    conn.commit()
    logger.info("Mock data loaded successfully.")


if __name__ == "__main__":
    create_tables()
    conn = get_db_connection()
    load_mock_data(conn)
    conn.close()
