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
    db, Students, Courses, Leaderboard  , AskHub
)
app = Flask(__name__, template_folder='Template')
app.secret_key = secrets.token_bytes(24)



db_path = os.path.join(os.path.dirname(__file__), "quiz.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
database_file = db_path 

db.init_app(app)

init_db()




    
      






from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from database import db, Students, Courses, Leaderboard

class AskHubModelView(ModelView):
    column_list = ['question', 'answer']
    form_columns = ['question', 'answer']

class StudentModelView(ModelView):
    column_list = ['name', 'email', 'age', 'grade', 'password', 'course_id']
    form_columns = ['name', 'email', 'age', 'grade', 'password', 'course_id']

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
    column_list = ['student_name', 'score', 'course_id', 'created_at']
    form_columns = ['student_name', 'score', 'course_id']


admin = Admin(app, name='Study Quiz Hub Admin')
admin.add_view(StudentModelView(Students, db.session))
admin.add_view(CourseModelView(Courses, db.session))
admin.add_view(LeaderboardModelView(Leaderboard, db.session))
admin.add_view(AskHubModelView(AskHub, db.session))

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


@app.route('/filter')
def filter_students():

    course_id = request.args.get('course_id')
    grade = request.args.get('grade')
    age = request.args.get('age')

    conn = get_db_connection()

    query = """
        SELECT students.*,
               courses.course_name
        FROM students
        LEFT JOIN courses
        ON students.course_id = courses.id
        WHERE 1=1
    """

    params = []

    if course_id:
        query += " AND students.course_id = ?"
        params.append(course_id)

    if age and age.isdigit():
       query += " AND students.age = ?"
       params.append(int(age))


    if grade:
       query += " AND LOWER(students.grade) = LOWER(?)"
       params.append(grade.strip())

    selected_course_name = "All Courses"

    course = None   # initialize first

    if course_id:
        course = conn.execute(
        "SELECT course_name FROM courses WHERE id=?",
        (course_id,)
    ).fetchone()

    if course:
     selected_course_name = course["course_name"]
    else:
     selected_course_name = "All Courses"

    students = conn.execute(query, params).fetchall()

    total_students = conn.execute(
    "SELECT COUNT(*) FROM students"
).fetchone()[0]
    
    total_students = conn.execute(
    "SELECT COUNT(*) FROM students"
).fetchone()[0]

    filtered_count = len(students)


    courses = conn.execute(
        "SELECT * FROM courses"
    ).fetchall()

    conn.close()
    

    return render_template(
        "student_table.html",
        students=students,
        courses=courses,
        selected_course=course_id,
        selected_age=age,
        selected_grade=grade,
        total_students=total_students,
        filtered_count=filtered_count,
        selected_course_name=selected_course_name
        
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
    quizzes = course_quizzes.get(course_name, [])
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
            
            return render_template(
                "quiz_result.html",
                name=session.get("student_name", ""),
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
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        course_id = request.form.get('course_id')
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
            "INSERT INTO students (name, email, age, grade, password, course_id, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, age_value, grade, hashed_password, course_id, "student")
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
        
        return render_template(
            'student_submitted.html',
            name=name,
            email=email,
            age=age,
            grade=grade,
            course_name=course_name,
        )

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

            # ✅ Database update
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
            session["email"] = student["email"]
            session["role"] = student["role"]
            flash(f"Welcome {student['name']} ✅ (Role: {student['role']})", "success")
            return redirect(url_for("choose_course"))
        else:
            flash("Invalid password ❌", "danger")

    return render_template("login.html", courses=get_courses())





@app.route('/logout')
def logout():
    student_id = session.get("student_id")

    user = None
    if student_id:
        
        user = get_student_by_id(student_id)

    
    session.clear()

    
    return render_template("logout.html", data=user)





    



@app.route('/students')
@app.route('/courses')
def student_table():
    students = get_students_with_courses()
    courses = get_courses()
    return render_template(
        'student_table.html',
        students=students,
        courses=courses
    )


from collections import defaultdict


@app.route('/student/<int:student_id>')
def view_student(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash('Student record not found.', 'warning')
        return redirect(url_for('student_table'))

    # Fetch all attempts
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

    total_attempts = sum(len(scores) for scores in grouped.values())
    return render_template('student_card.html', student=student, grouped=grouped , total_attempts=total_attempts)



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


@app.route("/score_history")
def score_history():
    history = get_score_history()
    attempts = get_attempt_counts()
    return render_template(
        "score_history.html",
        history=history,
        attempts=attempts
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


@app.route("/askhub", methods=["GET", "POST"])
def askhub():
    if request.method == "POST":
        user_message = request.form.get("message", "").strip().lower()

        # 1. Exact match
        result = AskHub.query.filter(AskHub.question.ilike(user_message)).first()
        if result:
            bot_reply = result.answer
            return render_template("askhub.html", reply=bot_reply)

        # 2. Partial match (contains full phrase)
        matches = AskHub.query.filter(AskHub.question.ilike(f"%{user_message}%")).all()
        if matches:
            # choose the longest question (closest to full match)
            best = max(matches, key=lambda m: len(m.question))
            bot_reply = best.answer
            return render_template("askhub.html", reply=bot_reply)

        # 3. Keyword match (split words and count overlap)
        keywords = user_message.split()
        keyword_matches = []
        for kw in keywords:
            keyword_matches += AskHub.query.filter(AskHub.question.ilike(f"%{kw}%")).all()

        if keyword_matches:
            # choose the question with most keyword overlap
            best = max(keyword_matches, key=lambda m: sum(kw in m.question.lower() for kw in keywords))
            bot_reply = best.answer
            return render_template("askhub.html", reply=bot_reply)

        # 4. Fallback
        bot_reply = "Sorry, I don’t know this yet ❌. Please ask the admin to add it."
        return render_template("askhub.html", reply=bot_reply)

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

    app.run(debug=True)

        