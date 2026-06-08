import os
import sqlite3

# Use a configurable database path. Set DATABASE_FILE to ':memory:' for no file persistence.
database_file = os.environ.get(
    "DATABASE_FILE",
    os.path.join(os.path.dirname(__file__), "quiz.db"),
)


def get_db_connection():
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT NOT NULL,
        description TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        age INTEGER,
        grade TEXT
    )
    """)
    conn.commit()

    column_info = conn.execute("PRAGMA table_info(students)").fetchall()
    if not any(col[1] == 'course_id' for col in column_info):
        conn.execute("ALTER TABLE students ADD COLUMN course_id INTEGER")
        conn.commit()

    if conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
        courses = [
            ("Python Basics", "Learn Python syntax and simple programs."),
            ("Web Development", "Create a basic website with Flask."),
            ("Data Science", "Analyze simple data and charts.")
        ]
        conn.executemany("INSERT INTO courses (course_name, description) VALUES (?, ?)", courses)
        conn.commit()
    conn.close()


def get_courses():
    conn = get_db_connection()
    courses = conn.execute("SELECT id, course_name FROM courses ORDER BY course_name").fetchall()
    conn.close()
    return courses


def get_students_with_courses():
    conn = get_db_connection()
    students = conn.execute(
        """
        SELECT students.id, students.name, students.email, students.age, students.grade,
               courses.course_name
        FROM students
        LEFT JOIN courses ON students.course_id = courses.id
        ORDER BY students.name
        """
    ).fetchall()
    conn.close()
    return students


def get_course_by_id(course_id):
    conn = get_db_connection()
    course = conn.execute("SELECT course_name FROM courses WHERE id = ?", (course_id,)).fetchone()
    conn.close()
    return course


def insert_student(name, email, age_value, grade, course_id=None):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO students (name, email, age, grade, course_id) VALUES (?, ?, ?, ?, ?)",
        (name, email, age_value, grade, course_id if course_id else None),
    )
    conn.commit()
    conn.close()
