import os
import secrets
from flask import Flask, render_template, request, session, redirect, url_for, flash
from database import (
    get_db_connection,
    init_db,
    get_courses,
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
)
app = Flask(__name__, template_folder='Template')
app.secret_key = secrets.token_bytes(24)
init_db()


def get_ranked_leaderboard(limit=5):
    top_entries = get_top_leaderboard(limit)
    for idx, entry in enumerate(top_entries, start=1):
        entry["rank"] = idx
    return top_entries

leaderboard_entries = get_ranked_leaderboard()

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
  
@app.route('/search')
def search_student():

    keyword = request.args.get('q', '')

    students = search_students(keyword)

    return render_template(
        'student_table.html',
        students=students
    )

def update_leaderboard(name, score, course_id=None):
    insert_leaderboard(name, score, course_id)
    updated_entries = get_ranked_leaderboard()
    leaderboard_entries.clear()
    leaderboard_entries.extend(updated_entries)



@app.route("/Quiz_page", methods=["GET", "POST"])
def Quiz_page():
    student_name = session.get("student_name")
    if not student_name:
        flash("Please register first before taking the quiz.", "warning")
        return redirect(url_for("student_form"))
    
    course_name = session.get("course_name")
    quizzes = course_quizzes.get(course_name, default_quizzes)
    total = len(quizzes)
    if "q_index" not in session:
        session["q_index"] = 0
        session["answers"] = []

    if request.method == "POST":
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

            update_leaderboard(student_name, score, session.get("course_id"))
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
                grade=grade,
                leaderboard=get_ranked_leaderboard()
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
    courses = get_courses()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        age = request.form.get('age', '').strip()
        grade = request.form.get('grade', '').strip()
        course_id = request.form.get('course_id')
        course_name = None

        if not name:
            flash('Student name is required.', 'danger')
            return render_template('student_form.html', courses=courses, form_data=request.form)

        if age and not age.isdigit():
            flash('Please enter a valid age.', 'warning')
            return render_template('student_form.html', courses=courses, form_data=request.form)

        age_value = int(age) if age.isdigit() else None
        insert_student(name, email, age_value, grade, course_id)
        session["student_name"] = name

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

        flash('Student registered successfully.', 'success')
        return render_template(
            'student_submitted.html',
            name=name,
            email=email,
            age=age,
            grade=grade,
            course_name=course_name,
        )

    return render_template('student_form.html', courses=courses)

@app.route('/students')
@app.route('/courses')
def student_table():
    students = get_students_with_courses()
    return render_template('student_table.html', students=students)

@app.route('/student/<int:student_id>')
def view_student(student_id):
    student = get_student_by_id(student_id)
    print(student)
    score_history = get_score_history()
    print(score_history)
    attempts=get_attempt_counts()
    print(attempts)
    latest_score = 0

    if score_history:
        latest_score = score_history[0]['score']

    if not student:
        flash('Student record not found.', 'warning')
        return redirect(url_for('student_table'))

    flash('Selected student details loaded.', 'info')
    return render_template(
        'student_card.html',
        name=student['name'],
        email=student['email'],
        age=student['age'],
        grade=student['grade'],
        course_name=student['course_name'],
        score=latest_score,
        attempts=attempts
    )
@app.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):

    student = get_student_by_id(student_id)

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        grade = request.form['grade']

        update_student(
            student_id,
            name,
            email,
            age,
            grade
        )

        flash("Student updated successfully!", "success")
        return redirect(url_for('view_student', student_id=student_id))

    return render_template(
        'edit_card.html',
        student=student
    )
@app.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student_record(student_id):
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


@app.route("/score_history")
def score_history():
    history = get_score_history()
    attempts = get_attempt_counts()
    return render_template(
        "score_history.html",
        history=history,
        attempts=attempts
    )
@app.route('/score_history/delete/<int:record_id>', methods=['POST'])
def delete_score_history(record_id):
    delete_score_record(record_id)
    flash("Record deleted successfully.", "success")
    return redirect(url_for('score_history'))


if __name__ == "__main__":
   app.run(debug=True)