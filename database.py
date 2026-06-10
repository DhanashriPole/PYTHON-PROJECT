import os
import sqlite3

database_file = os.environ.get(
    "DATABASE_FILE",
    os.path.join(os.path.dirname(__file__), "quiz.db"),
)


def get_db_connection():
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
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
        grade TEXT,
        course_id INTEGER,
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE SET NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        course_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE SET NULL
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


def get_student_by_id(student_id):
    conn = get_db_connection()
    student = conn.execute(
        """
        SELECT students.id, students.name, students.email, students.age, students.grade,
               courses.course_name
        FROM students
        LEFT JOIN courses ON students.course_id = courses.id
        WHERE students.id = ?
        """,
        (student_id,)
    ).fetchone()
    conn.close()
    return student


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


def delete_student(student_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def insert_leaderboard(student_name, score, course_id=None):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO leaderboard (student_name, score, course_id) VALUES (?, ?, ?)",
        (student_name, score, course_id if course_id else None),
    )
    conn.commit()
    conn.close()


def get_top_leaderboard(limit=5):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT student_name AS name, score FROM leaderboard ORDER BY score DESC, created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
