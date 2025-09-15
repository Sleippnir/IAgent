import sqlite3
from .database import get_db_connection

class SQLiteInterviewRepository:
    def __init__(self, db_connection):
        self._db = db_connection

    def get_role_by_id(self, role_id: str):
        cursor = self._db.cursor()
        cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
        role = cursor.fetchone()
        return role

    def get_questions_by_role_id(self, role_id: str):
        cursor = self._db.cursor()
        cursor.execute("SELECT * FROM questions WHERE role_id = ? ORDER BY order_index", (role_id,))
        questions = cursor.fetchall()
        return questions
