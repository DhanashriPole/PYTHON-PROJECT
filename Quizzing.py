import os
import json
import time
import re
import secrets
from flask import Flask, render_template, request,session, redirect, url_for, flash,jsonify
from groq import Groq
from datetime import datetime
from urllib.parse import quote
import os
import sys
import tempfile
import subprocess
import shutil
from dotenv import load_dotenv   
load_dotenv()
import os
from werkzeug.utils import secure_filename



from database import (
    get_db_connection,
    init_db,
    get_courses,
    fix_passwords,
    get_students_with_courses,
    get_course_by_id,
    insert_student,
    delete_student,
    get_student_by_id,
    insert_leaderboard,
    get_top_leaderboard,
    get_score_history,
    get_attempt_counts,
    delete_score_record,
    update_student,
    search_students,
    add_quiz_question,
    get_quiz_questions_by_course,
    db, Students, Courses, Leaderboard, AskHub, QuizQuestion
)
app = Flask(__name__, template_folder='Template')
app.secret_key = secrets.token_bytes(24)


UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLowed_Extensions=['pdf','png','jpg','jpeg','gif']
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLowed_Extensions





db_path = os.path.join(os.path.dirname(__file__), "quiz_backup.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
database_file = db_path 

db.init_app(app)

init_db()

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from database import db, Students, Courses, Leaderboard, AskHub, QuizQuestion
class AskHubModelView(ModelView):
    column_list = ['question', 'answer']
    form_columns = ['question', 'answer']

class StudentModelView(ModelView):
    column_list = ['name', 'email', 'age', 'grade', 'password', 'course_id', 'role', 'photo']
    form_columns = ['name', 'email', 'age', 'grade', 'password', 'course_id', 'role', 'photo']

    def on_model_change(self, form, model, is_created):
        from werkzeug.security import generate_password_hash

        
        if not model.password:
            model.password = generate_password_hash("default123")
        else:
            if not model.password.startswith("pbkdf2:sha256") and not model.password.startswith("scrypt:"):
                model.password = generate_password_hash(model.password)


        if not model.course_id:
            model.course_id = 1


        existing = Students.query.filter_by(email=model.email).first()

        
        if existing is not None and existing.id != model.id:
            raise ValueError("Email already exists ❌")

class CourseModelView(ModelView):
    column_list = ['course_name', 'description']
    form_columns = ['course_name', 'description']

class LeaderboardModelView(ModelView):
    column_list = ['student_name', 'score', 'time_taken', 'course_id', 'created_at']
    form_columns = ['student_name', 'score', 'time_taken', 'course_id']

class QuizQuestionModelView(ModelView):
    column_list = ['course_name', 'concept', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
    form_columns = ['course_name', 'concept', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']



admin = Admin(app, name='Study Quiz Hub Admin')
admin.add_view(StudentModelView(Students, db.session))
admin.add_view(CourseModelView(Courses, db.session))
admin.add_view(LeaderboardModelView(Leaderboard, db.session))
admin.add_view(AskHubModelView(AskHub, db.session))
admin.add_view(QuizQuestionModelView(QuizQuestion, db.session))

def add_askhub_data(question, answer):
    new_entry = AskHub(question=question.strip().lower(), answer=answer.strip())
    db.session.add(new_entry)
    db.session.commit()


def get_ranked_leaderboard(limit=5):
    top_entries = get_top_leaderboard(limit)
    for idx, entry in enumerate(top_entries, start=1):
        entry["rank"] = idx
    return top_entries

leaderboard_entries = get_ranked_leaderboard()


course_quizzes = {
    "Python Basics": [
        {
            "questions": "Which function is used to take input in Python?",
            "Option": ["A.print()", "B.input()", "C.len()", "D.str()"],
            "Answer": "B"
        },
        {
            "questions": "Which keyword is used to define a function?",
            "Option": ["A.def", "B.class", "C.import", "D.for"],
            "Answer": "A"
        },
        {
            "questions": "Which data type can store multiple values in Python?",
            "Option": ["A.int", "B.str", "C.list", "D.float"],
            "Answer": "C"
        },
        {
            "questions": "What is the correct file extension for Python files?",
            "Option": ["A.py", "B.java", "C.txt", "D.php"],
            "Answer": "A"
        },
        {
            "questions":"what is list in python?",
            "Option":["A.data type","B.EXCEPTION","C.string","D.data structure"],
            "Answer":"D"
        },
        {
            "questions":"what is tuple in python?",
            "Option":["A.data structure","B.data type","C.list","D.empty"],
            "Answer":"B "
        },
        {
            "questions":"what is dictionary in python?",
            "Option":["A.data structure","B.data type","C.list","D.tuple"],
            "Answer":"A"
        },
        {
            
           "questions": "What is exception handling in Python?",
           "Option": [
                      "A. A way to handle runtime errors using try-except blocks",
                      "B. A method to improve program speed",
                      "C. A technique to store data in key:value pairs",
                      "D. A process to convert Python code into machine code"
             ],
                       "Answer": "A"
        },
        {
              "questions": "Which keyword is used to handle exceptions in Python?",
                 "Option": [
                            "A. try",
                            "B. catch",
                            "C. error",
                            "D. handle"
                          ],
               "Answer": "A"
        },
        {
  "questions": "What happens if an exception is not handled in Python?",
  "Option": [
    "A. Program continues normally",
    "B. Program stops execution and shows an error",
    "C. Exception is ignored",
    "D. Python automatically fixes the error"
  ],
  "Answer": "B"
}



        
    ],
    "Web Development": [
        {
            "questions": "Which Python framework is used for building web applications?",
            "Option": ["A.Django", "B.numpy", "C.pandas", "D.matplotlib"],
            "Answer": "A"
        },
        {
            "questions": "In HTML, which tag is used for the largest heading?",
            "Option": ["A.<h1>", "B.<h2>", "C.<head>", "D.<title>"],
            "Answer": "A"
        },
        {
            "questions": "What does CSS stand for?",
            "Option": ["A.Cascading Style Sheets", "B.Computer Style Sheets", "C.Cool Style Syntax", "D.Code Style Sheet"],
            "Answer": "A"
        },
        {
            "questions": "Which method starts a Flask web server?",
            "Option": ["A.app.run()", "B.app.start()", "C.app.open()", "D.app.launch()"],
            "Answer": "A"
        },
        {
            "questions": "What is the correct file extension for HTML files?",
            "Option": ["A.html", "B.java", "C.txt", "D.php"],
            "Answer": "A"
        },
             {
        "questions": "Which HTML attribute is used to provide an alternate text for an image?",
       "Option": [
              "A. src",
               "B. alt",
              "C. title",
             "D. href"
               ],
              "Answer": "B"
        },
       {
                 "questions": "Which CSS property is used to change the text color?",
                  "Option": [
                           "A. font-color",
                           "B. text-color",
                           "C. color",
                           "D. background-color"
                         ],
                     "Answer": "C"
       },
        {
                 "questions": "Which CSS property is used to add a border to an element?",
                 "Option": [
                            "A. border",
                            "B. border-color",
                            "C. border-width",
                            "D. border-style"

                            ],
                 "Answer": "A"

        },
        {
                 "questions": "Which CSS property is used to change the background color?",
                 "Option": [
                            "A. background-color",
                            "B. background",
                            "C. color",
                            "D. font-color"
                          ],
                 "Answer": "A"
        },
        {
                 "questions": "Which CSS property is used to change the font size?",
                 "Option": [
                            "A. font-size",
                            "B. font-style",
                            "C. font-weight",
                            "D. font-family"
                          ],
                 "Answer": "A"
        }
    ],
    "Data Science": [
        {
            "questions": "Which library is commonly used for data analysis in Python?",
            "Option": ["A.pandas", "B.Flask", "C.PyGame", "D.TensorFlow"],
            "Answer": "A"
        },
        {
            "questions": "What does CSV stand for?",
            "Option": ["A.Comma Separated Values", "B.Computer Saved Values", "C.Call Separate Variables", "D.Coded System Values"],
            "Answer": "A"
        },
        {
            "questions": "Which plotting library is used to create charts in Python?",
            "Option": ["A.matplotlib", "B.requests", "C.os", "D.sys"],
            "Answer": "A"
        },
        {
            "questions": "What is the correct data structure for a table of rows and columns?",
            "Option": ["A.DataFrame", "B.String", "C.Set", "D.Int"],
            "Answer": "A"
        },
        {
            "questions": "What is the correct data structure for a list of values?",
            "Option": ["A.List", "B.String", "C.Set", "D.Int"],
            "Answer": "A"
        },
        {
    "questions": "Which Python library is used for numerical computations?",
    "Option": ["A.NumPy", "B.Flask", "C.Django", "D.Matplotlib"],
    "Answer": "A"
},
{
    "questions": "Which machine learning library is widely used in Python?",
    "Option": ["A.TensorFlow", "B.Pandas", "C.Seaborn", "D.SQLAlchemy"],
    "Answer": "A"
},
{
    "questions": "Which Python library is used for data visualization with statistical plots?",
    "Option": ["A.Seaborn", "B.Requests", "C.OS", "D.Scipy"],
    "Answer": "A"
},
{
    "questions": "Which file format is commonly used to store structured data?",
    "Option": ["A.JSON", "B.JPG", "C.MP3", "D.PNG"],
    "Answer": "A"
},
{
    "questions": "Which Python library is used for scientific computing?",
    "Option": ["A.SciPy", "B.Flask", "C.PyGame", "D.BeautifulSoup"],
    "Answer": "A"
}

    ],
    "CSS": [
        {
            "questions": "Which CSS property is used to change the text color?",
            "Option": ["A.color", "B.font-size", "C.background-color", "D.text-align"],
            "Answer": "A"
        },
        {
            "questions": "Which CSS property is used to add a border to an element?",
            "Option": ["A.border", "B.margin", "C.padding", "D.display"],
            "Answer": "A"
        },    
        {
            "questions": "Which CSS property is used to change the font size?",
            "Option": ["A.font-size", "B.color", "C.background-color", "D.text-align"],
            "Answer": "A"
        },
        {
            "questions": "Which CSS property is used to change the background color?",
            "Option": ["A.background-color", "B.color", "C.font-size", "D.text-align"],
            "Answer": "A"
        },
        {
            "questions": "Which CSS property is used to change the text alignment?",
            "Option": ["A.text-align", "B.color", "C.font-size", "D.background-color"],
            "Answer": "A"
        },
        {
    "questions": "Which CSS property is used to change the font style (italic, normal)?",
    "Option": ["A.font-style", "B.font-weight", "C.text-align", "D.text-decoration"],
    "Answer": "A"
},
{
    "questions": "Which CSS property controls the space inside an element’s border?",
    "Option": ["A.padding", "B.margin", "C.border", "D.spacing"],
    "Answer": "A"
},
{
    "questions": "Which CSS property controls the space outside an element’s border?",
    "Option": ["A.margin", "B.padding", "C.border", "D.spacing"],
    "Answer": "A"
},
{
    "questions": "Which CSS property is used to make text bold?",
    "Option": ["A.font-weight", "B.font-style", "C.text-transform", "D.text-decoration"],
    "Answer": "A"
},
{
    "questions": "Which CSS property is used to underline text?",
    "Option": ["A.text-decoration", "B.text-align", "C.font-style", "D.font-weight"],
    "Answer": "A"
}


    ],
    "Database" : [
        {
            "questions": "Which SQL keyword is used to create a table?",
            "Option": ["A.CREATE", "B.DROP", "C.ALTER", "D.SELECT"],
            "Answer": "A"
        },
        {
            "questions": "Which SQL keyword is used to insert data into a table?",
            "Option": ["A.INSERT", "B.DROP", "C.ALTER", "D.SELECT"],
            "Answer": "A"
        },
        {
            "questions": "Which SQL keyword is used to update data in a table?",
            "Option": ["A.UPDATE", "B.DROP", "C.ALTER", "D.SELECT"],
            "Answer": "A"
        },
        {
            "questions": "Which SQL keyword is used to delete data from a table?",
            "Option": ["A.DELETE", "B.DROP", "C.ALTER", "D.SELECT"],
            "Answer": "A"
        },    
        {
            "questions": "Which SQL keyword is used to select data from a table?",
            "Option": ["A.SELECT", "B.DROP", "C.ALTER", "D.UPDATE"],
            "Answer": "A"
        },
        {
    "questions": "Which SQL keyword is used to remove a table completely?",
    "Option": ["A.DROP", "B.DELETE", "C.REMOVE", "D.TRUNCATE"],
    "Answer": "A"
},
{
    "questions": "Which SQL clause is used to filter records?",
    "Option": ["A.WHERE", "B.ORDER BY", "C.GROUP BY", "D.HAVING"],
    "Answer": "A"
},
{
    "questions": "Which SQL keyword is used to sort the result set?",
    "Option": ["A.ORDER BY", "B.SORT", "C.ARRANGE", "D.GROUP BY"],
    "Answer": "A"
},
{
    "questions": "Which SQL function is used to count the number of rows?",
    "Option": ["A.COUNT()", "B.SUM()", "C.AVG()", "D.MAX()"],
    "Answer": "A"
},
{
    "questions": "Which SQL clause is used to group rows that have the same values?",
    "Option": ["A.GROUP BY", "B.ORDER BY", "C.WHERE", "D.HAVING"],
    "Answer": "A"
}

        
        
    ]
}


def normalize_option_text(option):
    if option.startswith(("A.", "B.", "C.", "D.")):
        return option.split(".", 1)[1].strip()
    return option.strip()


def load_quizzes_for_course(course_name):
    db_quizzes = get_quiz_questions_by_course(course_name)
    if db_quizzes:
        return [
            {
                "questions": quiz.question,
                "Option": [f"A.{quiz.option_a}", f"B.{quiz.option_b}", f"C.{quiz.option_c}", f"D.{quiz.option_d}"],
                "Answer": quiz.correct_option,
                "concept": quiz.concept or "General",
            }
            for quiz in db_quizzes
        ]
    return course_quizzes.get(course_name, [])


def seed_quiz_questions():
    if QuizQuestion.query.first():
        return

    for course_name, quizzes in course_quizzes.items():
        for quiz in quizzes:
            options = [normalize_option_text(opt) for opt in quiz["Option"]]
            add_quiz_question(
                course_name=course_name,
                question=quiz["questions"],
                options=options,
                correct_option=quiz["Answer"],
                concept=quiz.get("concept", "General"),
            )


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        admins = {
            "super@quizhub.com": {"password": "super123", "role": "superadmin"},
            "course@quizhub.com": {"password": "course123", "role": "courseadmin"},
            "leader@quizhub.com": {"password": "leader123", "role": "leaderadmin"}
        }
        
        if email in admins and admins[email]["password"] == password:
          session["role"] = admins[email]["role"]
          return redirect("/admin")
        else:
            flash("Invalid Admin Credentials ❌", "danger")
            return render_template("admin_login.html")

    return render_template("admin_login.html")


@app.route("/About_us")
def about_us():
    return render_template("About_us.html")


@app.route("/")
def home_page():
    conn = get_db_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_attempts = conn.execute(
        "SELECT COUNT(*) FROM leaderboard"
    ).fetchone()[0]

    total_courses = conn.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "home_page.html",
        total_students=total_students,
        total_attempts=total_attempts,
        total_courses=total_courses
    )
  
from flask import jsonify

@app.route('/search_suggestions')
def search_suggestions():

    keyword = request.args.get('q', '')

    students = search_students(keyword)

    results = []

    for student in students[:5]:
        results.append({
            "id": student["id"],
            "name": student["name"]
        })

    return jsonify(results)

from math import ceil

@app.route('/filter')
def filter_students():

    course_id = request.args.get('course_id')
    grade = request.args.get('grade')
    age = request.args.get('age')

    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_db_connection()

    # --------------------------
    # Base Query
    # --------------------------
    query = """
        SELECT DISTINCT
            students.*,
            courses.course_name
        FROM students
        LEFT JOIN courses
        ON students.course_id = courses.id
        WHERE 1=1
    """

    count_query = """
        SELECT COUNT(DISTINCT students.id)
        FROM students
        LEFT JOIN courses
        ON students.course_id = courses.id
        WHERE 1=1
    """

    params = []
    count_params = []

    # --------------------------
    # Filters
    # --------------------------
    if course_id:
        query += " AND students.course_id=?"
        count_query += " AND students.course_id=?"
        params.append(course_id)
        count_params.append(course_id)

    if age and age.isdigit():
        query += " AND students.age=?"
        count_query += " AND students.age=?"
        params.append(int(age))
        count_params.append(int(age))

    if grade:
        query += " AND LOWER(students.grade)=LOWER(?)"
        count_query += " AND LOWER(students.grade)=LOWER(?)"
        params.append(grade.strip())
        count_params.append(grade.strip())

    # --------------------------
    # Selected Course Name
    # --------------------------
    selected_course_name = "All Courses"

    if course_id:
        course = conn.execute(
            "SELECT course_name FROM courses WHERE id=?",
            (course_id,)
        ).fetchone()

        if course:
            selected_course_name = course["course_name"]

    # --------------------------
    # Filtered Count
    # --------------------------
    filtered_count = conn.execute(
        count_query,
        count_params
    ).fetchone()[0]

    # --------------------------
    # Pagination
    # --------------------------
    total_pages = max(1, ceil(filtered_count / per_page))

    query += """
        ORDER BY students.id DESC
        LIMIT ? OFFSET ?
    """

    students = conn.execute(
        query,
        params + [per_page, offset]
    ).fetchall()

    # --------------------------
    # Total Students
    # --------------------------
    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    # --------------------------
    # Courses
    # --------------------------
    courses = conn.execute(
        "SELECT * FROM courses ORDER BY course_name"
    ).fetchall()

    conn.close()

    return render_template(
        "student_table.html",
        students=students,
        courses=courses,
        selected_course=course_id,
        selected_age=age,
        selected_grade=grade,
        selected_course_name=selected_course_name,
        total_students=total_students,
        filtered_count=filtered_count,
        page=page,
        total_pages=total_pages
    )
def update_leaderboard(name, score, course_id=None, time_taken=0):
    insert_leaderboard(name, score, course_id, time_taken)
    updated_entries = get_ranked_leaderboard()
    leaderboard_entries.clear()
    leaderboard_entries.extend(updated_entries)


@app.route("/add_quiz_question", methods=["GET", "POST"])
def add_quiz_question_page():
    courses = get_courses()

    if request.method == "POST":
        course_name = request.form.get("course_name", "").strip()
        concept = request.form.get("concept", "").strip()
        question = request.form.get("question", "").strip()
        option_a = request.form.get("option_a", "").strip()
        option_b = request.form.get("option_b", "").strip()
        option_c = request.form.get("option_c", "").strip()
        option_d = request.form.get("option_d", "").strip()
        correct_option = request.form.get("correct_option", "").strip().upper()

        if not all([course_name, question, option_a, option_b, option_c, option_d]) or correct_option not in {"A", "B", "C", "D"}:
            flash("Please fill all fields and choose a valid correct option.", "danger")
            return render_template("add_quiz_question.html", courses=courses, form_data=request.form)

        add_quiz_question(
            course_name=course_name,
            question=question,
            options=[option_a, option_b, option_c, option_d],
            correct_option=correct_option,
            concept=concept,
        )
        flash("Quiz question added successfully ✅", "success")
        return redirect(url_for("add_quiz_question_page"))

    return render_template("add_quiz_question.html", courses=courses, form_data=None)


@app.route("/Quiz_page", methods=["GET", "POST"])
def Quiz_page():
    student_name = session.get("student_name")
    if not student_name:
        flash("Please register first before taking the quiz.", "warning")
        return redirect(url_for("student_form"))
    
    if request.args.get("again") == "1":
        session.pop("quiz_last_completed", None)
    elif request.method == "GET" and session.get("quiz_last_completed"):
        flash("Please choose a course before starting a new quiz.", "info")
        return redirect(url_for("choose_course"))

    course_name = session.get("course_name")
    if not course_name:
        flash("Please choose a course before starting the quiz.", "warning")
        return redirect(url_for("choose_course"))

    quizzes = load_quizzes_for_course(course_name)
    total = len(quizzes)
    if total == 0:
        flash("Please choose a valid course before starting the quiz.", "warning")
        return redirect(url_for("choose_course"))

    if "q_index" not in session:
        session["q_index"] = 0
        session["answers"] = []
        session["quiz_start_time"] = int(time.time())

    if request.method == "POST":
        answer = request.form.get("choice", "")
        answers = session.get("answers", [])
        answers.append(answer)
        session["answers"] = answers

        idx = session.get("q_index", 0)
        current_quiz = quizzes[idx]
        correct_letter = current_quiz["Answer"].upper()
        correct_option = next((opt for opt in current_quiz["Option"] if opt[0].upper() == correct_letter), correct_letter)
        selected_option = next((opt for opt in current_quiz["Option"] if opt[0].upper() == answer.upper()), answer)

        session["last_feedback"] = {
            "correct": answer.upper() == correct_letter,
            "selected": selected_option,
            "correct_option": correct_option
        }

        session["q_index"] = idx + 1

        if session["q_index"] >= total:
            score = 0
            attempted = sum(1 for a in answers if a)
            for idx2, a in enumerate(answers):
                if a and a.upper() == quizzes[idx2]["Answer"].upper():
                    score += 1

            start_time = session.get("quiz_start_time")
            time_taken = 0
            if start_time is not None:
                time_taken = max(0, int(time.time() - start_time))

            update_leaderboard(student_name, score, session.get("course_id"), time_taken)
            session["quiz_last_completed"] = True
            percentage = round(score / total * 100, 1)
            if percentage >= 90:
              grade = "A+"
            elif percentage >= 75:
             grade = "A"
            elif percentage >= 60:
             grade = "B"
            elif percentage >= 40:
              grade = "C"
            else:
             grade = "F"
            flash(f"Quiz complete! {student_name} scored {score}/{total}.", "success")
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            prompt = f"""
                    Student: {student_name}
                    Course: {course_name}
                    Score: {score}/{total}
                    Percentage: {percentage}%

                    plz provide study tip for student and short summary of student performance,it should not be more than 3 lines.
                 """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
            messages=[
           
               {
                   "role": "user",
                   "content": prompt
               }
             ]
          )
            ai_tip = response.choices[0].message.content
            session.pop("q_index", None)
            session.pop("answers", None)
            session.pop("quiz_start_time", None)
            session.pop("last_feedback", None)
            
            return render_template(
                "quiz_result.html",
                name=session.get("student_name", ""),
                score=score,
                attempted=attempted,
                total=total,
                percentage=percentage,
                grade=grade,
                duration=time_taken,
                leaderboard=get_ranked_leaderboard(),
                ai_tip=ai_tip
            )
            

        return redirect(url_for("Quiz_page"))

    idx = session.get("q_index", 0)
    quiz = quizzes[idx]
    feedback = session.pop("last_feedback", None)
    return render_template(
        "Quiz_page.html",
        quiz=quiz,
        idx=idx,
        total=total,
        student_name=session.get("student_name", ""),
        course_name=course_name,
        feedback=feedback,
    )

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    pdf_file = request.files["pdf_file"]
    if pdf_file:
        save_path = os.path.join("static/uploads", pdf_file.filename)
        pdf_file.save(save_path)
        return f"✅ PDF uploaded successfully: {pdf_file.filename}"
    return "❌ Upload failed"

@app.route("/Information")
def Study_quiz_hub():
    pdfs = os.listdir("static/uploads")
    return render_template("Study_quiz_hub.html", pdfs=pdfs)





@app.route('/student', methods=['GET', 'POST'])
def student_form():
    courses = get_courses()

    if request.method == 'POST':
                name = request.form.get('name', '').strip()
                email = request.form.get('email', '').strip()
                age = request.form.get('age', '').strip()
                grade = request.form.get('grade', '').strip()
                password = request.form.get('password', '').strip()
                confirm_password = request.form.get('confirm_password', '').strip()
                course_id = request.form.get('course_id')
                photo = request.files.get("photo")
                filename = "default.png"

                if photo and photo.filename != "":
                   if allowed_file(photo.filename):
                      filename = f"{int(time.time())}_{secure_filename(photo.filename)}"
                      

                      
                      save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                      
                      photo.save(save_path)
                      

                   else:
                      flash("Invalid image.", "danger")
                      return render_template('student_form.html', courses=courses, form_data=request.form)
                course_name = None

                if not name:
                   flash('Student name is required.', 'danger')
                   return render_template('student_form.html', courses=courses, form_data=request.form)

        
                if age and not age.isdigit():
                    flash('Please enter a valid age.', 'warning')
                    return render_template('student_form.html', courses=courses, form_data=request.form)

                age_value = int(age) if age.isdigit() else None

        
       
                conn = get_db_connection()
                existing = conn.execute("SELECT * FROM students WHERE email=?", (email,)).fetchone()

                if existing:
                     flash("Email already registered ❌ Please login instead.", "warning")
                     conn.close()
                     return redirect(url_for("login"))

                from werkzeug.security import generate_password_hash
                hashed_password = generate_password_hash(password)

        
                conn.execute(
                 "INSERT INTO students (name, email, age, grade, password, course_id, role, photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (name, email, age_value, grade, hashed_password, course_id, "student",filename),
                 )
                conn.commit()
                conn.close()

        
                session["student_name"] = name
                session["email"] = email
                session["role"] = "student"

                if course_id:
                   selected = get_course_by_id(course_id)
                   if selected:
                        course_name = selected["course_name"]
                        session["course_id"] = course_id
                        session["course_name"] = course_name
                   else:
                      session["course_id"] = None
                      session["course_name"] = None
                else:
                     session["course_id"] = None
                     session["course_name"] = None

                     flash('Student registered successfully ✅', 'success')
        
                return render_template('login.html')    

    return render_template("student_form.html", courses=courses)




@app.route('/choose_course', methods=['GET', 'POST'])
def choose_course():
    courses = get_courses()

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        selected = get_course_by_id(course_id)

        if selected:
            session['course_id'] = course_id
            session['course_name'] = selected['course_name']
            session.pop('quiz_last_completed', None)
            session.pop('q_index', None)
            session.pop('answers', None)
            session.pop('quiz_start_time', None)
            session.pop('last_feedback', None)

            
            email = session.get('email')
            if email:
                conn = get_db_connection()
                conn.execute("UPDATE students SET course_id=? WHERE email=?", (course_id, email))
                conn.commit()
                conn.close()

            flash(f"Course '{selected['course_name']}' selected ✅", "success")
            return redirect(url_for('Quiz_page'))
        else:
            flash("Invalid course selection ❌", "danger")

    return render_template('choose_course.html', courses=courses)


def generate_quiz(course_name, num_questions=10):

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    prompt = f"""
Generate exactly {num_questions} multiple choice questions for the course "{course_name}".

Return ONLY valid JSON.

Format:

[
  {{
    "Question":"What is Python?",
    "Option":[
      "A) Programming Language",
      "B) Database",
      "C) Browser",
      "D) Operating System"
    ],
    "Answer":"A"
  }}
]

Do not return markdown.
Do not return explanation.
Do not return code block.
 Return EXACTLY {num_questions} questions.
 Do NOT return fewer than {num_questions}.

"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text = response.choices[0].message.content.strip()

        print("\n================ RAW RESPONSE ================\n")
        print(text)

        
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

    
        start = text.find("[")
        end = text.rfind("]")

        if start == -1 or end == -1:
            raise Exception("JSON array not found")

        text = text[start:end+1]

        # Remove trailing commas
        text = re.sub(r",\s*}", "}", text)
        text = re.sub(r",\s*]", "]", text)

        quizzes = json.loads(text)

        result = []

        for q in quizzes:

            result.append({

                "questions": q.get("Question", ""),

                "Option": q.get("Option", []),

                "Answer": q.get("Answer", "A").upper(),

                "concept": "AI Generated"

            })

        print("\n================ PARSED QUIZ ================\n")
        print(result)

        return result

    except Exception as e:

        print("AI ERROR:", e)

        flash("AI quiz generation failed due to format error.", "danger")

        return [

            {
                "questions": "What is HTML?",
                "Option": [
                    "A) Language",
                    "B) Protocol",
                    "C) Database",
                    "D) OS"
                ],
                "Answer": "A",
                "concept": "General"
            },

            {
                "questions": "CSS stands for?",
                "Option": [
                    "A) Cascading Style Sheets",
                    "B) Computer Style System",
                    "C) Code Syntax Sheet",
                    "D) Color Style Source"
                ],
                "Answer": "A",
                "concept": "General"
            }

        ]


@app.route("/ai_quiz_page", methods=["GET", "POST"])
def ai_quiz_page():
    
    if request.method == "POST" and request.form.get("course_id"):
        course_id = request.form.get("course_id")
        selected = get_course_by_id(course_id)
        if selected:
            session["course_id"] = course_id
            session["course_name"] = selected["course_name"]


    student_name = session.get("student_name")
    if not student_name:
        flash("Please register first before taking the quiz.", "warning")
        return redirect(url_for("student_form"))

    course_name = session.get("course_name")
    if not course_name:
        flash("Please choose a course before starting the quiz.", "warning")
        return redirect(url_for("choose_course"))

    
    if "ai_quizzes" not in session:
        quizzes = generate_quiz(course_name, num_questions=10)
        if not quizzes:
            flash("AI quiz could not be generated ❌ Try again later.", "danger")
            return redirect(url_for("choose_course"))
        session["ai_quizzes"] = quizzes
        session["q_index"] = 0
        session["answers"] = []
        session["quiz_start_time"] = int(time.time())
    else:
        quizzes = session["ai_quizzes"]

    total = len(quizzes)

    
    if request.method == "POST":
        answer = request.form.get("choice", "")
        if not answer:
            flash("Please select an answer before proceeding.", "warning")
            return redirect(url_for("ai_quiz_page"))

        answers = session.get("answers", [])
        answers.append(answer)
        session["answers"] = answers

        idx = session.get("q_index", 0)
        current_quiz = quizzes[idx]
        correct_letter = current_quiz["Answer"].upper()
        correct_option = next((opt for opt in current_quiz["Option"] if opt[0].upper() == correct_letter), correct_letter)
        selected_option = next((opt for opt in current_quiz["Option"] if opt[0].upper() == answer.upper()), answer)

        session["last_feedback"] = {
            "correct": answer.upper() == correct_letter,
            "selected": selected_option,
            "correct_option": correct_option
        }

        session["q_index"] = idx + 1

        
        if session["q_index"] >= total:
            score = 0
            attempted = sum(1 for a in answers if a)
            for idx2, a in enumerate(answers):
                if a and a.upper() == quizzes[idx2]["Answer"].upper():
                    score += 1

            start_time = session.get("quiz_start_time")
            time_taken = 0
            if start_time is not None:
                time_taken = max(0, int(time.time() - start_time))

            update_leaderboard(student_name, score, session.get("course_id"), time_taken)
            session["quiz_last_completed"] = True
            percentage = round(score / total * 100, 1)

            if percentage >= 90:
                grade = "A+"
            elif percentage >= 75:
                grade = "A"
            elif percentage >= 60:
                grade = "B"
            elif percentage >= 40:
                grade = "C"
            else:
                grade = "F"

            flash(f"AI Quiz complete! {student_name} scored {score}/{total}.", "success")

            
            client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            prompt = f"""
                Student: {student_name}
                Course: {course_name}
                Score: {score}/{total}
                Percentage: {percentage}%

                plz provide study tip for student and short summary of student performance,it should not be more than 3 lines.
            """
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_tip = response.choices[0].message.content

            
            session.pop("ai_quizzes", None)
            session.pop("q_index", None)
            session.pop("answers", None)
            session.pop("quiz_start_time", None)
            session.pop("last_feedback", None)

            return render_template(
                "quiz_result.html",
                name=student_name,
                score=score,
                attempted=attempted,
                total=total,
                percentage=percentage,
                grade=grade,
                duration=time_taken,
                leaderboard=get_ranked_leaderboard(),
                ai_tip=ai_tip
            )

        return redirect(url_for("ai_quiz_page"))

    
    idx = session.get("q_index", 0)

    quizzes = session.get("ai_quizzes", [])

    if not quizzes:
       flash("No quiz found.", "warning")
       return redirect(url_for("choose_course"))

    if idx >= len(quizzes):
       idx = 0
       session["q_index"] = 0
    quiz = quizzes[idx]
    feedback = session.pop("last_feedback", None)

    return render_template(
    "Quiz_page.html",
    quiz=quiz,
    idx=idx,
    total=len(quizzes),
    student_name=student_name,
    course_name=course_name,
    feedback=feedback
)
    





from werkzeug.security import check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        student = conn.execute("SELECT * FROM students WHERE email=?", (email,)).fetchone()
        conn.close()

        if not student:
            flash("Email not found ❌ Please register first.", "warning")
            return redirect(url_for("student_form"))

        from werkzeug.security import check_password_hash

        if check_password_hash(student["password"], password):
            session["student_id"] = student["id"]
            session["student_name"] = student["name"]
            session["student_photo"] = student["photo"]
            session["email"] = student["email"]
            session["role"] = student["role"]
            flash(f"Welcome {student['name']} ✅ (Role: {student['role']})", "success")
            return redirect(url_for("choose_course"))
        else:
            flash("Invalid password ❌", "danger")

    return render_template("login.html", courses=get_courses())


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email address.", "danger")
            return redirect(url_for("forgot_password"))

       
        student = Students.query.filter_by(email=email).first()

        if not student:
            flash("No account found with this email address.", "danger")
            return redirect(url_for("forgot_password"))

       
        session["reset_email"] = email

        return redirect(url_for("reset_password"))

    return render_template("forgot_password.html")

from werkzeug.security import check_password_hash, generate_password_hash
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():

   
    email = session.get("reset_email")

    if not email:
        flash("Please start the password reset process again.", "warning")
        return redirect(url_for("forgot_password"))

    student = Students.query.filter_by(email=email).first()

    if not student:
        session.pop("reset_email", None)

        flash("Account not found.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        
        if not password or not confirm_password:

            flash(
                "Please enter and confirm your new password.",
                "danger"
            )

            return redirect(url_for("reset_password"))

        # Password mismatch
        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(url_for("reset_password"))

       
        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(url_for("reset_password"))

        # Hash new password
        student.password = generate_password_hash(password)

        db.session.commit()

        # Remove reset session
        session.pop("reset_email", None)

        flash(
            "Password reset successfully! You can now login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template(
        "reset_password.html",
        email=email
    )
@app.route('/logout')
def logout():
    student_id = session.get("student_id")

    user = None
    if student_id:
        
        user = get_student_by_id(student_id)

    
    session.clear()

    
    return render_template("Logout.html", data=user)





    



from math import ceil

@app.route('/students')
@app.route('/courses')
def student_table():

    page = request.args.get("page", 1, type=int)
    per_page = 10

    conn = get_db_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_pages = ceil(total_students / per_page)

    offset = (page - 1) * per_page

    students = conn.execute("""
        SELECT students.*,
               courses.course_name
        FROM students
        LEFT JOIN courses
        ON students.course_id = courses.id
        LIMIT ? OFFSET ?
    """, (per_page, offset)).fetchall()

    courses = conn.execute(
        "SELECT * FROM courses"
    ).fetchall()

    conn.close()

    return render_template(
        "student_table.html",
        students=students,
        courses=courses,
        page=page,
        total_pages=total_pages
    )
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
def generate_performance_summary(student_name, results):

    if not results:
        return "No quiz attempts found for this student."

    total_attempts = len(results)
    highest_score = max(r.score for r in results)
    average_score = sum(r.score for r in results) / total_attempts

    performance = "\n".join(
        [f"{r.course_name}: {r.score}/10" for r in results]
    )

    prompt = f"""
You are an expert teacher.

Analyze this student's quiz performance.

Student Name: {student_name}

Total Attempts: {total_attempts}
Highest Score: {highest_score}/10
Average Score: {average_score:.1f}/10

Course Scores:
{performance}

Write a professional report in about 80-120 words.

Include:
1. Performance Summary
2. Strengths
3. Weaknesses
4. Recommendations
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(e)
        return "AI summary could not be generated."

from collections import defaultdict


@app.route('/student/<int:student_id>')
def view_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash('Student record not found.', 'warning')
        return redirect(url_for('student_table'))

    results = db.session.query(
        Courses.course_name,
        Leaderboard.score,
        Leaderboard.created_at
    ).join(Courses, Courses.id == Leaderboard.course_id) \
     .filter(Leaderboard.student_name == student['name']) \
     .order_by(Courses.course_name, Leaderboard.created_at) \
     .all()

    # Group by course
    grouped = defaultdict(list)
    for r in results:
        grouped[r.course_name].append(r.score)

    
    highest_score = max((max(scores) for scores in grouped.values() if scores), default=0)

    all_scores = [score for scores in grouped.values() for score in scores]

    average_score = round(sum(all_scores)/len(all_scores),1) if all_scores else 0

    total_attempts = len(all_scores)
    if all_scores:
        ai_summary = generate_performance_summary(student["name"],results)
    else:
        ai_summary = "This student has not attempted any quiz yet."
    return render_template('student_card.html', student=student, grouped=grouped , total_attempts=total_attempts,highest_score=highest_score,
                                             average_score=average_score,
                                                                         ai_summary=ai_summary)
@app.route("/change_photo/<int:student_id>", methods=["GET", "POST"])
def change_photo(student_id):

    if request.method == "POST":
        photo = request.files["photo"]

        if photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            conn = get_db_connection()
            conn.execute(
                "UPDATE students SET photo=? WHERE id=?",
                (filename, student_id)
            )
            conn.commit()
            conn.close()

            flash("Profile photo updated successfully.", "success")
            

        return redirect(url_for("view_student", student_id=student_id))

    return render_template("change_photo.html", student_id=student_id)


@app.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if session.get("role") != "admin":
        flash("❌only admin can edit", "danger")
        return redirect(url_for('student_table'))

    student = get_student_by_id(student_id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        grade = request.form['grade']

        update_student(student_id, name, email, age, grade)
        flash("Student updated successfully!", "success")
        return redirect(url_for('view_student', student_id=student_id))

    return render_template('edit_card.html', student=student)
@app.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student_record(student_id):
    if session.get("role") != "admin":
        flash("❌ only admin can delete", "danger")
        return redirect(url_for('student_table'))

    student = get_student_by_id(student_id)
    if not student:
        flash('Student record not found.', 'warning')
    else:
        delete_student(student_id)
        flash(f"Student '{student['name']}' deleted successfully.", 'success')
    return redirect(url_for('student_table'))
@app.route("/leaderboard")
def leaderboard_page():
    top_entries = get_top_leaderboard()
    for idx, entry in enumerate(top_entries, start=1):
        entry["rank"] = idx
    return render_template("leaderboard.html", leaderboard=top_entries)



from math import ceil

@app.route("/score_history")
def score_history():

    page = request.args.get("page", 1, type=int)
    per_page = 10

    conn = get_db_connection()

    total_records = conn.execute(
        "SELECT COUNT(*) FROM leaderboard"
    ).fetchone()[0]

    total_pages = ceil(total_records / per_page)

    offset = (page - 1) * per_page

    history = conn.execute("""
SELECT
    l.*,
    c.course_name,
    (
        SELECT COUNT(*)
        FROM leaderboard x
        WHERE x.student_name = l.student_name
    ) AS attempts
FROM leaderboard l
LEFT JOIN courses c
ON c.id = l.course_id
ORDER BY l.created_at DESC
LIMIT ? OFFSET ?
""", (per_page, offset)).fetchall()
    for row in history:
      print(dict(row))

    conn.close()

    attempts = get_attempt_counts()

    return render_template(
        "score_history.html",
        history=history,
        attempts=attempts,
        page=page,
        total_pages=total_pages
    )

@app.before_request
def restrict_admin():
    if request.path.startswith("/admin") and not request.path.startswith("/admin_login"):
        if "role" not in session:
            return redirect("/admin_login")


@app.route('/score_history/delete/<int:record_id>', methods=['POST'])
def delete_score_history(record_id):
    delete_score_record(record_id)
    flash("Record deleted successfully.", "success")
    return redirect(url_for('score_history'))

from functools import wraps

def student_page_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        student_id = session.get("student_id")
        
        if not student_id:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))

        
        return f(*args, **kwargs)

    return decorated_function
@app.route("/askhub", methods=["GET", "POST"])
@student_page_required
def askhub():

    if request.method == "POST":

        user_message = request.form.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a question."})

       
        result = AskHub.query.filter(
            AskHub.question.ilike(user_message)
        ).first()

        if result:
            return jsonify({
                "reply": result.answer
            })

        matches = AskHub.query.filter(
            AskHub.question.ilike(f"%{user_message}%")
        ).all()

        if matches:
            best = max(matches, key=lambda x: len(x.question))

            return jsonify({
                "reply": best.answer
            })

      
        try:

            client = Groq(
                api_key=os.environ.get("GROQ_API_KEY")
            )

            response = client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[
                    {
                        "role":"system",
                        "content":"""
You are Study Quiz Hub AI Tutor.

Answer in simple English.

Keep answers within 8 lines.

Explain programming questions with examples.
"""
                    },
                    {
                        "role":"user",
                        "content":user_message
                    }
                ]
            )

            ai_reply = response.choices[0].message.content

            return jsonify({
                "reply": ai_reply
            })

        except Exception as e:

            print(e)

            return jsonify({
                "reply":"Sorry, AI is currently unavailable."
            })

    return render_template("askhub.html")



@app.route("/askhub_add", methods=["GET", "POST"])
def askhub_add():
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        answer = request.form.get("answer", "").strip()

        if not question or not answer:
            flash("Both question and answer are required ❌", "danger")
            return render_template("askhub_add.html")

        add_askhub_data(question, answer)
        flash("AskHub Q&A added successfully ✅", "success")
        return redirect(url_for("askhub_add"))

    return render_template("askhub_add.html")

@app.route("/exam_roadmap", methods=["GET", "POST"])
@student_page_required
def exam_roadmap():

    if request.method == "POST":

        exam_name = request.form.get("exam_name", "").strip()
        exam_date = request.form.get("exam_date", "").strip()
        subjects = request.form.get("subjects", "").strip()
        daily_hours = request.form.get("daily_hours", "").strip()

        if not exam_name or not exam_date or not subjects or not daily_hours:
            flash("Please fill all fields.", "warning")
            return render_template(
                "exam_roadmap.html",
                generated=False
            )

        try:
            daily_hours = float(daily_hours)

            if daily_hours <= 0 or daily_hours > 16:
                raise ValueError

        except ValueError:
            flash(
                "Please enter valid daily study hours between 1 and 16.",
                "danger"
                )
            return render_template(
                "exam_roadmap.html",
                generated=False
            )

        try:
            exam_date_obj = datetime.strptime(
                exam_date,
                "%Y-%m-%d"
            ).date()

            today = datetime.now().date()
            days_remaining = (exam_date_obj - today).days

        except ValueError:
            flash(
                "Please enter a valid exam date.",
                "danger"
            )
            return render_template(
                "exam_roadmap.html",
                generated=False
            )

        if days_remaining < 0:
            flash(
                "Exam date cannot be in the past.",
                "danger"
            )
            return render_template(
                "exam_roadmap.html",
                generated=False
            )

        if days_remaining == 0:
            flash(
                "Your exam is today. No preparation days are available.",
                "warning"
            )
            return render_template(
                "exam_roadmap.html",
                generated=False
            )

        today_display = today.strftime("%d %B %Y")
        exam_display = exam_date_obj.strftime("%d %B %Y")

        prompt = f"""
You are an expert exam preparation planner.

Create a personalized and realistic exam preparation roadmap.

TODAY:
{today_display}

EXAM DATE:
{exam_display}

NUMBER OF PREPARATION DAYS:
{days_remaining}

EXAM NAME:
{exam_name}

SUBJECTS:
{subjects}

DAILY STUDY HOURS:
{daily_hours}

The student has exactly {days_remaining} preparation days.

The roadmap MUST contain exactly {days_remaining} days.

Today is the first preparation day.

The exam date itself MUST NOT be included as a study day.

For example, if today is 12 August and exam date is 15 August:

Day 1 = 12 August
Day 2 = 13 August
Day 3 = 14 August
15 August = EXAM DAY

Generate exactly 3 roadmap entries in this example.

The roadmap should intelligently divide the subjects across the available days.

Include:

1. Daily topics
2. Study hours
3. Practice questions
4. Revision
5. Mock tests when appropriate
6. Weak topic improvement
7. Final revision
8. Exam preparation tips

Do not create extra days.
Do not create fewer days.
Do not include the exam date in the roadmap.
Use realistic study hours.
Distribute subjects properly.
Give more attention to difficult or important topics.
Include revision before the exam.
If only 1-3 days are available, create an intensive revision plan.
If many days are available, gradually cover topics and include mock tests.

RETURN ONLY VALID JSON.

Do NOT return markdown.
Do NOT return ```json.
Do NOT return explanations outside JSON.

Use exactly this structure:

{{
    "exam_name": "{exam_name}",
    "exam_date": "{exam_date}",
    "days_remaining": {days_remaining},
    "overview": "Short preparation strategy",
    "roadmap": [
        {{
            "day": 1,
            "date": "YYYY-MM-DD",
            "topics": [
                "Topic 1",
                "Topic 2"
            ],
            "study_hours": {daily_hours},
            "practice": "Practice questions related to today's topics",
            "revision": "Revise today's topics"
        }}
    ],
    "final_tips": [
        "Tip 1",
        "Tip 2",
        "Tip 3",
        "Tip 4",
        "Tip 5"
    ]
}}
"""

        try:

            api_key = os.environ.get("GROQ_API_KEY")

            if not api_key:
                raise Exception(
                    "GROQ_API_KEY environment variable is missing."
                )

            client = Groq(
                api_key=api_key
            )

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an expert exam preparation AI.

Create realistic, practical and personalized study plans.

When JSON is requested:
- Return ONLY valid JSON.
- Do not use markdown.
- Do not use ```json.
- Do not add explanations.
- Follow the requested JSON structure exactly.
"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )

            text = response.choices[0].message.content.strip()

            print("\n========== AI ROADMAP RESPONSE ==========\n")
            print(text)

            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1:
                raise Exception(
                    "JSON object not found in AI response."
                )

            text = text[start:end + 1]

            text = re.sub(
                r",\s*}",
                "}",
                text
            )

            text = re.sub(
                r",\s*]",
                "]",
                text
            )

            roadmap = json.loads(text)

            print("\n========== PARSED ROADMAP ==========\n")
            print(roadmap)

            if "roadmap" not in roadmap:
                raise Exception(
                    "Roadmap data missing."
                )

            if not isinstance(roadmap["roadmap"], list):
                raise Exception(
                    "Invalid roadmap format."
                )

            if len(roadmap["roadmap"]) != days_remaining:
                raise Exception(
                    f"AI generated {len(roadmap['roadmap'])} days "
                    f"instead of {days_remaining} days."
                )

            if "final_tips" not in roadmap:
                roadmap["final_tips"] = []

            return render_template(
                "exam_roadmap.html",
                roadmap=roadmap,
                generated=True
            )

        except json.JSONDecodeError as e:

            print("\n========== JSON ERROR ==========")
            print(e)

            flash(
                "AI returned an invalid roadmap. Please try again.",
                "danger"
            )

            return render_template(
                "exam_roadmap.html",
                generated=False
            )

        except Exception as e:

            print("\n========== ROADMAP ERROR ==========")
            print(e)

            flash(
                "AI roadmap generation failed. Please try again.",
                "danger"
            )

            return render_template(
                "exam_roadmap.html",
                generated=False
            )

    return render_template(
        "exam_roadmap.html",
        generated=False
    )



def student_api_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("student_id") or session.get("role") != "student":
            return jsonify({
                "success": False,
                "error": "Please login as a student to use Code Lab."
            }), 401

        return f(*args, **kwargs)

    return decorated_function
@app.route("/code_lab")
@student_page_required
def code_lab():
    return render_template("code_lab.html")
@app.route("/run_code", methods=["POST"])
@student_api_required
def run_code():

    try:
        data = request.get_json() or {}

        code = data.get("code", "")
        language = data.get("language", "python").lower().strip()
        input_data = data.get("input", "")

        if not code.strip():
            return jsonify({
                "success": False,
                "error": "Please enter some code."
            })

        allowed_languages = [
            "python",
            "c",
            "cpp",
            "c++",
            "java",
            "javascript",
            "js"
        ]

        if language not in allowed_languages:
            return jsonify({
                "success": False,
                "error": "Unsupported language."
            })

        with tempfile.TemporaryDirectory() as temp_dir:

            if language == "python":

                file_path = os.path.join(
                    temp_dir,
                    "program.py"
                )

                with open(
                    file_path,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                result = subprocess.run(
                    ["python", file_path],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=temp_dir
                )

            elif language == "c":

                source_file = os.path.join(
                    temp_dir,
                    "program.c"
                )

                output_file = os.path.join(
                    temp_dir,
                    "program.exe"
                )

                with open(
                    source_file,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                compile_result = subprocess.run(
                    [
                        "gcc",
                        source_file,
                        "-o",
                        output_file
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )

                if compile_result.returncode != 0:
                    return jsonify({
                        "success": False,
                        "error": compile_result.stderr
                    })

                result = subprocess.run(
                    [output_file],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=temp_dir
                )

            elif language in ["cpp", "c++"]:

                source_file = os.path.join(
                    temp_dir,
                    "program.cpp"
                )

                output_file = os.path.join(
                    temp_dir,
                    "program.exe"
                )

                with open(
                    source_file,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                compile_result = subprocess.run(
                    [
                        "g++",
                        source_file,
                        "-o",
                        output_file
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )

                if compile_result.returncode != 0:
                    return jsonify({
                        "success": False,
                        "error": compile_result.stderr
                    })

                result = subprocess.run(
                    [output_file],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=temp_dir
                )

            elif language == "java":

                source_file = os.path.join(
                    temp_dir,
                    "Main.java"
                )

                with open(
                    source_file,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                compile_result = subprocess.run(
                    [
                        "javac",
                        source_file
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir
                )

                if compile_result.returncode != 0:
                    return jsonify({
                        "success": False,
                        "error": compile_result.stderr
                    })

                result = subprocess.run(
                    [
                        "java",
                        "Main"
                    ],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=temp_dir
                )

            elif language in ["javascript", "js"]:

                file_path = os.path.join(
                    temp_dir,
                    "program.js"
                )

                with open(
                    file_path,
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(code)

                result = subprocess.run(
                    [
                        "node",
                        file_path
                    ],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=temp_dir
                )

            else:

                return jsonify({
                    "success": False,
                    "error": "Unsupported language."
                })

            if result.returncode == 0:

                return jsonify({
                    "success": True,
                    "output": result.stdout
                })

            return jsonify({
                "success": False,
                "error": result.stderr or result.stdout
            })

    except subprocess.TimeoutExpired:

        return jsonify({
            "success": False,
            "error": "Execution time exceeded."
        })

    except FileNotFoundError as e:

        return jsonify({
            "success": False,
            "error": "Required compiler or runtime is not installed: " + str(e)
        })

    except Exception as e:

        print("Code execution error:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        })
@app.route("/generate_coding_questions", methods=["POST"])
@student_api_required
def generate_coding_questions():

    try:
        data = request.get_json() or {}

        language = data.get("language", "Python")
        difficulty = data.get("difficulty", "Easy")
        count = int(data.get("count", 5))

        # Safety limit
        count = max(1, min(count, 10))

        prompt = f"""
Generate {count} high-quality programming practice questions.

Programming Language: {language}
Difficulty: {difficulty}

Each question MUST contain all of these fields:

- title
- description
- input
- output
- example_input
- example_output
- constraints
- hint

IMPORTANT:
1. Never leave any field empty.
2. example_input must contain a real example.
3. example_output must contain the correct output for that example.
4. constraints must contain realistic constraints.
5. hint must provide a useful hint without giving the complete solution.
6. The question must be appropriate for the selected programming language.
7. Return ONLY valid JSON.
8. Do NOT use markdown code fences.

Return exactly this structure:

[
    {{
        "title": "Sum of Numbers in a List",
        "description": "Write a program to calculate the sum of all numbers in a given list.",
        "input": "A list of integers.",
        "output": "The sum of all integers in the list.",
        "example_input": "[1, 2, 3, 4, 5]",
        "example_output": "15",
        "constraints": "1 <= n <= 1000",
        "hint": "Use a loop or the built-in sum function."
    }}
]
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programming question generator."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        ai_response = response.choices[0].message.content.strip()

       
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]

        if ai_response.startswith("```"):
            ai_response = ai_response[3:]

        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]

        ai_response = ai_response.strip()

        questions = json.loads(ai_response)

        return jsonify({
            "success": True,
            "questions": questions
        })

    except Exception as e:

        print("Coding Question Generation Error:", repr(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
def generate_fun_quiz(course_name, num_questions=10):
    prompt = f"""
Create {num_questions} multiple-choice quiz questions for the subject "{course_name}".

Return ONLY valid JSON.
Do not add markdown.
Do not add ```json.
Do not add explanations.

The JSON must be an array like this:

[
  {{
    "Question": "What is ...?",
    "A": "Option A",
    "B": "Option B",
    "C": "Option C",
    "D": "Option D",
    "Answer": "A"
  }}
]

Rules:
- Exactly {num_questions} questions.
- Every question must have A, B, C and D.
- Answer must contain ONLY A, B, C or D.
- Questions must be related to {course_name}.
- Make questions suitable for students.
- Feel like kids questions.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quiz generator. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=5000
        )

        content = response.choices[0].message.content.strip()

        print("\n===== FUN QUIZ AI RESPONSE =====")
        print(content)
        print("================================\n")

        
        if content.startswith("```"):
            content = re.sub(r"```(?:json)?", "", content)
            content = content.replace("```", "").strip()

       
        start = content.find("[")
        end = content.rfind("]")

        if start == -1 or end == -1:
            print("FUN QUIZ: JSON ARRAY NOT FOUND")
            return []

        content = content[start:end + 1]

        quizzes = json.loads(content)

        if not isinstance(quizzes, list):
            print("FUN QUIZ: RESPONSE IS NOT A LIST")
            return []

        valid_quizzes = []

        for q in quizzes:

            if not isinstance(q, dict):
                continue

            question = str(q.get("Question", "")).strip()
            option_a = str(q.get("A", "")).strip()
            option_b = str(q.get("B", "")).strip()
            option_c = str(q.get("C", "")).strip()
            option_d = str(q.get("D", "")).strip()

            answer = str(
                q.get("Answer", "")
            ).strip().upper()

            answer = answer.replace(".", "").strip()

            if answer.startswith("OPTION "):
                answer = answer.replace(
                    "OPTION ",
                    "",
                    1
                ).strip()

            if answer not in ["A", "B", "C", "D"]:
                continue

            if not question:
                continue

            if not option_a or not option_b:
                continue

            if not option_c or not option_d:
                continue

            valid_quizzes.append({
                "Question": question,
                "A": option_a,
                "B": option_b,
                "C": option_c,
                "D": option_d,
                "Answer": answer
            })

        print(
            "VALID FUN QUIZ QUESTIONS:",
            len(valid_quizzes)
        )

        return valid_quizzes[:num_questions]

    except json.JSONDecodeError as e:

        print(
            "FUN QUIZ JSON ERROR:",
            repr(e)
        )

        return []

    except Exception as e:

        print(
            "FUN QUIZ GENERATION ERROR:",
            repr(e)
        )

        return []
@app.route("/fun_quiz", methods=["GET", "POST"])
@student_page_required
def fun_quiz():

    student_name = session.get("student_name")

    if not student_name:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    if request.args.get("new") == "1":

        session.pop("fun_quizzes", None)
        session.pop("fun_q_index", None)
        session.pop("fun_answers", None)
        session.pop("fun_score", None)
        session.pop("fun_course", None)
        session.pop("fun_course_id", None)
        session.pop("fun_voice_message", None)

        return redirect(url_for("fun_quiz"))

    if request.method == "POST":

        action = request.form.get("action", "").strip()

        if action == "start_quiz":

            selected_course_id = request.form.get(
                "course_id", ""
            ).strip()

            if not selected_course_id:
                flash(
                    "Please select a course first.",
                    "warning"
                )
                return redirect(url_for("fun_quiz"))

            try:
                course_id = int(selected_course_id)
            except (ValueError, TypeError):
                flash(
                    "Invalid course selected.",
                    "danger"
                )
                return redirect(url_for("fun_quiz"))

            course = Courses.query.filter_by(
                id=course_id
            ).first()

            if not course:
                flash(
                    "Selected course was not found.",
                    "danger"
                )
                return redirect(url_for("fun_quiz"))

            course_name = course.course_name

            session.pop("fun_quizzes", None)
            session.pop("fun_q_index", None)
            session.pop("fun_answers", None)
            session.pop("fun_score", None)
            session.pop("fun_voice_message", None)

            try:

                quizzes = generate_fun_quiz(
                    course_name,
                    num_questions=10
                )

            except Exception as e:

                print(
                    "FUN QUIZ AI ERROR:",
                    repr(e)
                )

                flash(
                    "AI could not generate the quiz. Please try again.",
                    "danger"
                )

                return redirect(url_for("fun_quiz"))

            if not quizzes or not isinstance(quizzes, list):

                print(
                    "FUN QUIZ INVALID RESPONSE:",
                    quizzes
                )

                flash(
                    "AI could not generate questions. Please try again.",
                    "danger"
                )

                return redirect(url_for("fun_quiz"))

            valid_quizzes = []

            for q in quizzes:

                if not isinstance(q, dict):
                    continue

                question = str(
                    q.get("Question", "")
                ).strip()

                option_a = str(
                    q.get("A", "")
                ).strip()

                option_b = str(
                    q.get("B", "")
                ).strip()

                option_c = str(
                    q.get("C", "")
                ).strip()

                option_d = str(
                    q.get("D", "")
                ).strip()

                answer = str(
                    q.get("Answer", "")
                ).strip().upper()

                answer = answer.replace(".", "").strip()

                if answer.startswith("OPTION "):
                    answer = answer.replace(
                        "OPTION ",
                        "",
                        1
                    ).strip()

                if answer not in ["A", "B", "C", "D"]:
                    continue

                if not question:
                    continue

                if not option_a:
                    continue

                if not option_b:
                    continue

                if not option_c:
                    continue

                if not option_d:
                    continue

                valid_quizzes.append({
                    "Question": question,
                    "A": option_a,
                    "B": option_b,
                    "C": option_c,
                    "D": option_d,
                    "Answer": answer
                })

            if not valid_quizzes:

                print(
                    "NO VALID FUN QUIZ QUESTIONS:",
                    quizzes
                )

                flash(
                    "AI generated invalid questions. Please try again.",
                    "danger"
                )

                return redirect(
                    url_for("fun_quiz")
                )

            valid_quizzes = valid_quizzes[:10]

            session["fun_quizzes"] = valid_quizzes
            session["fun_q_index"] = 0
            session["fun_answers"] = []
            session["fun_score"] = 0
            session["fun_course"] = course_name
            session["fun_course_id"] = course_id
            session.pop("fun_voice_message", None)

            return redirect(
                url_for("fun_quiz")
            )

        elif action == "answer":

            quizzes = session.get(
                "fun_quizzes",
                []
            )

            if not quizzes:

                flash(
                    "Please start a quiz first.",
                    "warning"
                )

                return redirect(
                    url_for("fun_quiz")
                )

            idx = session.get(
                "fun_q_index",
                0
            )

            total = len(quizzes)

            if idx < 0 or idx >= total:

                return redirect(
                    url_for("fun_quiz")
                )

            answer = str(
                request.form.get("choice", "")
            ).strip().upper()

            if answer not in ["A", "B", "C", "D"]:

                flash(
                    "Please choose an answer.",
                    "warning"
                )

                return redirect(
                    url_for("fun_quiz")
                )

            current_quiz = quizzes[idx]

            correct_answer = str(
                current_quiz.get("Answer", "")
            ).strip().upper()

            correct_answer = correct_answer.replace(
                ".",
                ""
            ).strip()

            if correct_answer.startswith("OPTION "):

                correct_answer = correct_answer.replace(
                    "OPTION ",
                    "",
                    1
                ).strip()

            print(
                "QUESTION:",
                current_quiz.get("Question")
            )

            print(
                "USER ANSWER:",
                answer
            )

            print(
                "CORRECT ANSWER:",
                correct_answer
            )

            answers = session.get(
                "fun_answers",
                []
            )

            answers.append({
                "question": current_quiz.get("Question"),
                "selected": answer,
                "correct": correct_answer,
                "is_correct": answer == correct_answer
            })

            session["fun_answers"] = answers

            if answer == correct_answer:

                session["fun_score"] = (
                    session.get("fun_score", 0) + 1
                )

                feedback_message = (
                    "🎉 Excellent! Correct answer! Keep it up!"
                )

                voice_message = (
                    "Excellent! Correct answer! Keep it up!"
                )

                flash(
                    feedback_message,
                    "success"
                )

            else:

                feedback_message = (
                    f"😊 Nice try! The correct answer was option {correct_answer}."
                )

                voice_message = (
                    f"Nice try! The correct answer was option {correct_answer}."
                )

                flash(
                    feedback_message,
                    "info"
                )

            session["fun_voice_message"] = voice_message

            idx += 1

            session["fun_q_index"] = idx

            if idx >= total:

                score = session.get(
                    "fun_score",
                    0
                )

                percentage = round(
                    (score / total) * 100,
                    1
                ) if total > 0 else 0

                if percentage >= 90:

                    message = (
                        "🏆 Amazing! You are a Quiz Superstar!"
                    )

                elif percentage >= 75:

                    message = (
                        "🌟 Great job! Keep learning!"
                    )

                elif percentage >= 50:

                    message = (
                        "😊 Good effort! You are improving!"
                    )

                else:

                    message = (
                        "🚀 Keep practicing! You can do it!"
                    )

                course_name = session.get(
                    "fun_course",
                    "Fun Quiz"
                )

                course_id = session.get(
                    "fun_course_id"
                )

                try:
                    course_id = int(course_id)
                except (ValueError, TypeError):
                    course_id = None

                if course_id:

                    try:

                        update_leaderboard(
                            student_name,
                            score,
                            course_id,
                            0
                        )

                    except Exception as e:

                        print(
                            "LEADERBOARD UPDATE ERROR:",
                            repr(e)
                        )

                session["fun_result"] = {
                    "name": student_name,
                    "score": score,
                    "total": total,
                    "percentage": percentage,
                    "message": message,
                    "course_name": course_name
                }

                session.pop("fun_quizzes", None)
                session.pop("fun_q_index", None)
                session.pop("fun_answers", None)
                session.pop("fun_score", None)
                session.pop("fun_course", None)
                session.pop("fun_course_id", None)

                return redirect(
                    url_for("fun_quiz_result")
                )

            return redirect(
                url_for("fun_quiz")
            )

        else:

            flash(
                "Invalid quiz request.",
                "danger"
            )

            return redirect(
                url_for("fun_quiz")
            )

    quizzes = session.get(
        "fun_quizzes"
    )

    if quizzes:

        idx = session.get(
            "fun_q_index",
            0
        )

        total = len(quizzes)

        if 0 <= idx < total:

            quiz = quizzes[idx]

            return render_template(
                "fun_quiz.html",
                quiz=quiz,
                idx=idx,
                total=total,
                student_name=student_name,
                course_name=session.get(
                    "fun_course"
                ),
                voice_message=session.get(
                    "fun_voice_message"
                )
            )

    courses = Courses.query.order_by(
        Courses.course_name.asc()
    ).all()

    return render_template(
        "fun_quiz.html",
        quiz=None,
        courses=courses,
        student_name=student_name,
        course_name=None
    )


@app.route("/fun_quiz_result")
@student_page_required
def fun_quiz_result():

    result = session.get("fun_result")

    if not result:
        return redirect(
            url_for("fun_quiz")
        )

    return render_template(
        "fun_quiz_result.html",
        name=result.get("name"),
        score=result.get("score", 0),
        total=result.get("total", 0),
        percentage=result.get("percentage", 0),
        message=result.get("message"),
        course_name=result.get(
            "course_name",
            "Fun Quiz"
        )
    )


@app.route("/clear_fun_voice", methods=["POST"])
@student_page_required
def clear_fun_voice():

    session.pop(
        "fun_voice_message",
        None
    )

    return jsonify({
        "success": True
    })
@app.route("/ai_interview", methods=["GET", "POST"])
@student_page_required
def ai_interview():

    student_name = session.get("student_name")

    if not student_name:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    

    if request.args.get("new") == "1":

        session.pop("ai_interview_messages", None)
        session.pop("ai_interview_subject", None)
        session.pop("ai_interview_role", None)
        session.pop("ai_interview_mode", None)
        session.pop("ai_interview_started", None)

        return redirect(url_for("ai_interview"))

    

    if request.method == "POST":

        data = request.get_json(silent=True) or {}

        action = data.get("action")

        

        if action == "start":

            subject = data.get(
                "subject",
                "Mixed Computer Engineering"
            )

            role = data.get(
                "role",
                "Computer Engineering Student"
            )

            mode = data.get(
                "mode",
                "Technical Interview"
            )

            session["ai_interview_subject"] = subject
            session["ai_interview_role"] = role
            session["ai_interview_mode"] = mode
            session["ai_interview_started"] = True
            session["ai_interview_messages"] = []

            system_prompt = f"""
You are a realistic professional AI interviewer.

You are interviewing a Computer Engineering student.

INTERVIEW DETAILS

Role:
{role}

Subject:
{subject}

Interview Mode:
{mode}


YOUR BEHAVIOR

You are an interviewer, not a teacher.

This is a practice interview for learning and confidence.

Rules:

1. Ask only ONE question at a time.

2. Start naturally.

3. Begin with an easy question.

4. Gradually increase difficulty.

5. Adapt questions according to the student's answers.

6. Do not give marks.

7. Do not give numerical scores.

8. Do not mention leaderboards.

9. Do not create a final ranking.

10. Do not save interview history.

11. Give short natural feedback after an answer.

12. If the answer is correct:
   briefly acknowledge it.

13. If the answer is partially correct:
   explain what is missing in one or two sentences.

14. If the answer is incorrect:
   do not embarrass the student.
   Give a small hint and continue.

15. Occasionally ask practical questions.

16. For programming subjects, ask conceptual,
    debugging and real-world questions.

17. For project interviews, ask about:
    project purpose,
    technologies,
    student's contribution,
    challenges,
    database,
    testing and deployment.

18. For HR interviews, ask realistic student-level
    questions about communication, goals, teamwork
    and problem solving.

19. Keep responses suitable for being spoken aloud.

20. Do not write long paragraphs.

21. Never repeat a question that has already been asked.

Start the interview.

Introduce yourself briefly and ask the first question.
"""

            try:

                response = client.chat.completions.create(

                    model="llama-3.3-70b-versatile",

                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ],

                    temperature=0.7,
                    max_tokens=300
                )

                ai_response = (
                    response.choices[0]
                    .message.content
                    .strip()
                )

                session["ai_interview_messages"] = [
                    {
                        "role": "assistant",
                        "content": ai_response
                    }
                ]

                session.modified = True

                return jsonify({
                    "success": True,
                    "message": ai_response
                })

            except Exception as e:

                print("AI INTERVIEW START ERROR:", e)

                return jsonify({
                    "success": False,
                    "error":
                    "AI interviewer is temporarily unavailable."
                }), 500

        

        elif action == "answer":

            answer = data.get("answer", "").strip()

            input_type = data.get(
                "input_type",
                "voice"
            )

            if not answer:

                return jsonify({
                    "success": False,
                    "error": "No answer detected."
                }), 400

            messages = session.get(
                "ai_interview_messages",
                []
            )

            subject = session.get(
                "ai_interview_subject",
                "Mixed Computer Engineering"
            )

            role = session.get(
                "ai_interview_role",
                "Computer Engineering Student"
            )

            mode = session.get(
                "ai_interview_mode",
                "Technical Interview"
            )

           

            system_prompt = f"""
You are conducting a realistic Computer Engineering
mock interview.

Role:
{role}

Subject:
{subject}

Mode:
{mode}


The student's latest answer was obtained through
microphone speech recognition.

The text may contain:

- minor grammar mistakes
- repeated words
- incomplete sentences
- speech recognition mistakes

Understand the student's intended meaning instead of
judging grammar harshly.


INTERVIEW RULES

- Speak naturally.
- Be professional but friendly.
- Ask ONE question at a time.
- Do not give marks.
- Do not give numerical scores.
- Do not mention leaderboards.
- Do not save history.
- Do not produce a final score.
- Give brief feedback.
- Ask the next relevant question.
- Adapt difficulty based on the student's response.
- Do not repeat questions.
- Keep answers short enough to be spoken aloud.

If the answer is good:

Briefly acknowledge it and continue.

If partially correct:

Say what was missing and ask a related question.

If incorrect:

Politely explain the basic concept briefly,
then continue with another suitable question.

The goal is practice, confidence and learning.
"""

            conversation = [

                {
                    "role": "system",
                    "content": system_prompt
                }

            ]

            
            conversation.extend(messages)

            conversation.append({

                "role": "user",

                "content": (
                    "[Student answered using microphone]\n\n"
                    + answer
                )

            })

            try:

                response = client.chat.completions.create(

                    model="llama-3.3-70b-versatile",

                    messages=conversation,

                    temperature=0.7,

                    max_tokens=350
                )

                ai_response = (
                    response.choices[0]
                    .message.content
                    .strip()
                )

                
                messages.append({

                    "role": "user",

                    "content": (
                        "[Voice Answer]\n" + answer
                    )

                })

                messages.append({

                    "role": "assistant",

                    "content": ai_response
                })

                session[
                    "ai_interview_messages"
                ] = messages

                session.modified = True

                return jsonify({

                    "success": True,

                    "message": ai_response,

                    "input_type": input_type
                })

            except Exception as e:

                print(
                    "AI INTERVIEW ANSWER ERROR:",
                    e
                )

                return jsonify({

                    "success": False,

                    "error":
                    "Unable to process your answer."
                }), 500

        

        elif action == "end":

            session.pop(
                "ai_interview_messages",
                None
            )

            session.pop(
                "ai_interview_subject",
                None
            )

            session.pop(
                "ai_interview_role",
                None
            )

            session.pop(
                "ai_interview_mode",
                None
            )

            session.pop(
                "ai_interview_started",
                None
            )

            return jsonify({

                "success": True,

                "message":
                "Great practice! 🚀"
            })

        return jsonify({

            "success": False,

            "error":
            "Invalid interview action."

        }), 400

   

    subjects = [
        "Python",
        "C Programming",
        "C++",
        "Java",
        "HTML & CSS",
        "JavaScript",
        "Web Development",
        "SQL & DBMS",
        "Data Structures & Algorithms",
        "Computer Networks",
        "Operating Systems",
        "Digital Electronics",
        "Microprocessors & Microcontrollers",
        "Computer Architecture",
        "Cyber Security Basics",
        "Artificial Intelligence & ML Basics",
        "Linux",
        "Git & GitHub",
        "Mixed Computer Engineering"
    ]

    interview_modes = [
        "Technical Interview",
        "HR Interview",
        "Rapid Fire",
        "Project Interview",
        "Mixed Interview"
    ]

    return render_template(
        "ai_interview.html",
        student_name=student_name,
        subjects=subjects,
        interview_modes=interview_modes
    )



@app.route("/ai_lectures")
def ai_lectures():
    return render_template("ai_lectures.html")




@app.route("/generate_ai_lecture", methods=["POST"])
def generate_ai_lecture():

    try:

        data = request.get_json() or {}

        course = data.get("course", "").strip()
        topic = data.get("topic", "").strip()
        level = data.get("level", "Beginner").strip()
        language = data.get("language", "English").strip()
        style = data.get("style", "Visual and practical").strip()

        

        if not course or not topic:

            return jsonify({
                "success": False,
                "error": "Please select a course and enter a topic."
            }), 400


       

        prompt = f"""
You are an expert educational teacher and lecture creator.

Create a high-quality educational lecture for students.

Course: {course}
Topic: {topic}
Level: {level}
Language: {language}
Teaching Style: {style}

IMPORTANT:
The lecture will be displayed as a text-based learning session.

Do NOT create images.
Do NOT create image prompts.
Do NOT mention image generation.
Do NOT include visual prompts.

The lecture must be:

- Accurate
- Student friendly
- Easy to understand
- Well structured
- Step-by-step
- Engaging
- Useful for exams and practical learning

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "title": "Lecture title",

    "introduction": "Short engaging introduction",

    "duration": "Approximate duration",

    "learning_objectives": [
        "objective 1",
        "objective 2",
        "objective 3"
    ],

    "sections": [
        {{
            "heading": "Section heading",

            "explanation": "Detailed but easy-to-understand explanation of this part of the topic.",

            "example": "Useful example related to this section."
        }}
    ],

    "key_points": [
        "important point 1",
        "important point 2",
        "important point 3"
    ],

    "summary": "Clear lecture summary"
}}

IMPORTANT RULES:

1. Create 4 to 6 sections.

2. Every section must explain a different part of the topic.

3. Use simple student-friendly language.

4. Explain difficult concepts step-by-step.

5. For programming topics, include correct code examples where useful.

6. For programming examples, keep code technically correct.

7. For hardware topics, explain components and working clearly.

8. For networking topics, explain concepts with simple real-world examples.

9. For DBMS topics, explain tables, keys, queries and relationships when relevant.

10. For mathematics, explain formulas and solve examples step-by-step.

11. Do not invent facts.

12. Do not use markdown outside the JSON.

13. The response MUST be valid JSON.

14. Do not add ```json or ``` around the response.
"""


        

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are an expert educational teacher. "
                        "Return accurate educational lectures "
                        "strictly in valid JSON format."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.5,

            max_tokens=7000
        )


        

        result = response.choices[0].message.content.strip()


       

        if result.startswith("```"):

            result = result.replace("```json", "")
            result = result.replace("```", "")
            result = result.strip()


        

        lecture = json.loads(result)


        

        required_fields = [
            "title",
            "introduction",
            "duration",
            "learning_objectives",
            "sections",
            "key_points",
            "summary"
        ]

        for field in required_fields:

            if field not in lecture:

                raise ValueError(
                    f"AI response is missing field: {field}"
                )


       

        session["ai_lecture"] = lecture

        session.modified = True


        

        return jsonify({

            "success": True,

            "redirect_url": url_for(
                "ai_lecture_session"
            )

        })


    

    except json.JSONDecodeError:

        print("AI returned invalid JSON.")

        return jsonify({

            "success": False,

            "error":
                "AI returned an invalid lecture format. "
                "Please try again."

        }), 500


    

    except Exception as e:

        print(
            "AI Lecture Error:",
            str(e)
        )

        return jsonify({

            "success": False,

            "error":
                "Unable to generate the lecture right now. "
                "Please try again."

        }), 500





@app.route("/ai_lecture_session")
def ai_lecture_session():

    lecture = session.get("ai_lecture")


    # If no lecture exists, go back to generator

    if not lecture:

        return redirect(
            url_for("ai_lectures")
        )


    return render_template(

        "ai_lecture_session.html",

        lecture=lecture

    )





@app.route("/clear_ai_lecture")
def clear_ai_lecture():

    session.pop(
        "ai_lecture",
        None
    )

    return redirect(
        url_for("ai_lectures")
    )
if __name__ == "__main__":
   
    
    with app.app_context():
        db.create_all()

        if not Courses.query.first():
            default_courses = [
                Courses(course_name='Python Basics', description='Learn Python syntax and simple programs.'),
                Courses(course_name='Web Development', description='Create a basic website with Flask.'),
                Courses(course_name='Data Science', description='Analyze simple data and charts.')
            ]
            db.session.add_all(default_courses)
            db.session.commit()

        seed_quiz_questions()

    app.run(debug=True)

    #updated again 