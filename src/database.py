
import sqlite3
import os

# Find the project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATA_DIR, "students.db")


def connect_database():
    """Connect to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)


def create_table():
    """Create the student table."""
    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                marks REAL NOT NULL
            )
        """)


def add_student(student_id, name, class_name,
                gender, phone, marks):
    """Add a new student record."""
    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO students
            (student_id, name, class_name, gender, phone, marks)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, name, class_name,
              gender, phone, marks))


def get_all_students():
    """Retrieve all student records."""
    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM students ORDER BY id DESC
        """)

        return cursor.fetchall()


def search_students(keyword):
    """Search students by ID, name or class."""
    with connect_database() as connection:
        cursor = connection.cursor()

        search = f"%{keyword}%"

        cursor.execute("""
            SELECT * FROM students
            WHERE student_id LIKE ?
            OR name LIKE ?
            OR class_name LIKE ?
            ORDER BY id DESC
        """, (search, search, search))

        return cursor.fetchall()


def update_student(record_id, student_id, name,
                   class_name, gender, phone, marks):
    """Update an existing student record."""
    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE students
            SET student_id = ?,
                name = ?,
                class_name = ?,
                gender = ?,
                phone = ?,
                marks = ?
            WHERE id = ?
        """, (student_id, name, class_name,
              gender, phone, marks, record_id))


def delete_student(record_id):
    """Delete a student record."""
    with connect_database() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM students WHERE id = ?
        """, (record_id,))
