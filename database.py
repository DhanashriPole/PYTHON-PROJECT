
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
    if not any(col[1] == 'password' for col in column_info):
       conn.execute("ALTER TABLE students ADD COLUMN password TEXT")
    conn.commit()

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




from werkzeug.security import generate_password_hash

def insert_student(name, email, age_value, grade, password, course_id=None):
    conn = get_db_connection()
    hashed_password = generate_password_hash(password)
    conn.execute(
        """INSERT INTO students (name, email, age, grade, password, course_id) VALUES (?, ?, ?, ?, ?, ?)""",
        (name, email, age_value, grade, hashed_password, course_id if course_id else None),
    )
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def insert_leaderboard( student_name, score, course_id=None):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO leaderboard (student_name, score, course_id) VALUES (?, ?, ?)",
        ( student_name, score, course_id if course_id else None),
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

def get_score_history():
   conn = get_db_connection()

   rows = conn.execute("""
                 SELECT 
                   id, 
               student_name,
                score,
                 created_at
                FROM leaderboard
        ORDER BY created_at DESC
    """).fetchall()
   
   conn.close()
   return rows

def get_attempt_counts():
    conn = get_db_connection()

    rows = conn.execute("""
        SELECT student_name,
               COUNT(*) AS attempts
        FROM leaderboard
        GROUP BY student_name
        ORDER BY attempts DESC
    """).fetchall()

    conn.close()
    return rows

def get_score_history():
    conn = get_db_connection()

    rows = conn.execute("""
        SELECT 
            id,
                student_name,
               score,
               created_at,
               COUNT(*) OVER (PARTITION BY student_name) AS attempts
        FROM leaderboard
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return rows
def delete_score_record(record_id):
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM leaderboard WHERE id=?",
        (record_id,)
    )
    conn.commit()
    conn.close()
def update_student(student_id, name, email, age, grade):
    conn = get_db_connection()

    conn.execute("""
        UPDATE students
        SET name = ?,
            email = ?,
            age = ?,
            grade = ?
        WHERE id = ?
    """, (name, email, age, grade, student_id))

    conn.commit()
    conn.close()
def search_students(keyword):
    conn = get_db_connection()

    students = conn.execute("""
        SELECT students.id,
               students.name,
               students.email,
               students.age,
               students.grade,
               courses.course_name
        FROM students
        LEFT JOIN courses ON students.course_id = courses.id
        WHERE students.name LIKE ?
    """, (f"%{keyword}%",)).fetchall()

    conn.close()
    return students





from werkzeug.security import generate_password_hash

conn = get_db_connection()
students = conn.execute("SELECT id, password FROM students").fetchall()

for s in students:
    pwd = s["password"]

    
    if not pwd:
        continue

    
    if pwd.startswith("pbkdf2:sha256") or pwd.startswith("scrypt:"):
        continue

    
    hashed = generate_password_hash(pwd)
    conn.execute("UPDATE students SET password=? WHERE id=?", (hashed, s["id"]))

conn.commit()
conn.close()

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50))
    age = db.Column(db.Integer)
    grade = db.Column(db.String(10))
    password = db.Column(db.String(200))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    created_at = db.Column(db.String, default="CURRENT_TIMESTAMP")
