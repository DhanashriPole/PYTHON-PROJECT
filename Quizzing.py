import os
import secrets
from flask import Flask, render_template, request, session, redirect, url_for
from database import init_db, get_courses, get_students_with_courses, get_course_by_id, insert_student
app = Flask(__name__, template_folder='Template')
app.secret_key = secrets.token_bytes(24)

init_db()

leaderboard_entries = [
    {"rank": 1, "name": "Aarti", "score": 5},
    {"rank": 2, "name": "Kaveri", "score": 4},
    {"rank": 3, "name": "Divya", "score": 4},
    {"rank": 4, "name": "Rohini", "score": 3},
    {"rank": 5, "name": "Sowmya", "score": 2}
]

default_quizzes = [
    {
        "questions": "Which function is used to take input in Python?",
        "Option": ["A.print()", "B.input()", "C.len()", "D.str()"],
        "Answer": "B"
    },
    {
        "questions": "Which Python data structure stores values in key:value pair?",
        "Option": ["A.List", "B.Tuple", "C.Dictionary", "D.String"],
        "Answer": "C"
    },
    {
        "questions": "Who invented Python?",
        "Option": ["A.James Gosling", "B.Dennis Ritchie", "C.Guido van Rossum", "D.Bill Gates"],
        "Answer": "C"
    },
    {
        "questions": "For printing many records, which concept is used in Python?",
        "Option": ["A.list", "B.Tuple", "C.set", "D.LOOP"],
        "Answer": "D"
    },
    {
        "questions": "Which keyword is used to define a function in Python?",
        "Option": ["A.def", "B.numpy", "C.pandas", "D.function"],
        "Answer": "A"
    }
]

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
        }
    ]
}
@app.route("/")
def home_page():
    return render_template('home_page.html')

def update_leaderboard(name, score):
    
    leaderboard_entries.append({"name": name, "score": score})
    leaderboard_entries.sort(key=lambda item: item["score"], reverse=True)
    top_entries = leaderboard_entries[:5]
    for idx, entry in enumerate(top_entries, start=1):
        entry["rank"] = idx
    leaderboard_entries.clear()
    leaderboard_entries.extend(top_entries)

@app.route("/Quiz_page", methods=["GET", "POST"])
def Quiz_page():
    course_name = session.get("course_name")
    quizzes = course_quizzes.get(course_name, default_quizzes)
    total = len(quizzes)
    if "q_index" not in session:
        session["q_index"] = 0
        session["answers"] = []
        session["student_name"] = ""

    if request.method == "POST":
        student_name = request.form.get("student_name", "Guest").strip() or "Guest"
        session["student_name"] = student_name
        answer = request.form.get("choice", "")
        answers = session.get("answers", [])
        answers.append(answer)
        session["answers"] = answers

        session["q_index"] = session.get("q_index", 0) + 1

        if session["q_index"] >= total:
            score = 0
            attempted = sum(1 for a in answers if a)
            for idx, a in enumerate(answers):
                if a and a.upper() == quizzes[idx]["Answer"].upper():
                    score += 1

            update_leaderboard(student_name, score)
            percentage = round(score / total * 100, 1)
            session.pop("q_index", None)
            session.pop("answers", None)
            session.pop("student_name", None)
            return render_template(
                "quiz_result.html",
                name=student_name,
                score=score,
                attempted=attempted,
                total=total,
                percentage=percentage,
                leaderboard=leaderboard_entries,
            )

        return redirect(url_for("Quiz_page"))

    idx = session.get("q_index", 0)
    quiz = quizzes[idx]
    return render_template(
        "Quiz_page.html",
        quiz=quiz,
        idx=idx,
        total=total,
        student_name=session.get("student_name", ""),
        course_name=course_name,
    )

@app.route("/Information")
def Study_quiz_hub():
    return render_template("Study_quiz_hub.html")


@app.route('/student', methods=['GET', 'POST'])
def student_form():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        age = request.form.get('age', '').strip()
        grade = request.form.get('grade', '').strip()
        course_id = request.form.get('course_id')
        course_name = None

        if age.isdigit():
            age_value = int(age)
        else:
            age_value = None

        insert_student(name, email, age_value, grade, course_id)

        if course_id:
            selected = get_course_by_id(course_id)
            if selected:
                course_name = selected["course_name"]
                session["course_id"] = course_id
                session["course_name"] = course_name
            else:
                session.pop("course_id", None)
                session.pop("course_name", None)
        else:
            session.pop("course_id", None)
            session.pop("course_name", None)

        return render_template(
            'student_submitted.html',
            name=name,
            email=email,
            age=age,
            grade=grade,
            course_name=course_name,
        )

    courses = get_courses()
    return render_template('student_form.html', courses=courses)

@app.route('/students')
@app.route('/courses')
def student_table():
    students = get_students_with_courses()
    return render_template('student_table.html', students=students)

@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html", leaderboard=leaderboard_entries)

if __name__ == "__main__":
   app.run(debug=True)