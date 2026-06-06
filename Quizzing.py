import secrets
from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__, template_folder='Template')
app.secret_key = secrets.token_bytes(24)

leaderboard_entries = [
    {"rank": 1, "name": "Aarti", "score": 5},
    {"rank": 2, "name": "Kaveri", "score": 4},
    {"rank": 3, "name": "Divya", "score": 4},
    {"rank": 4, "name": "Rohini", "score": 3},
    {"rank": 5, "name": "Sowmya", "score": 2}
]

Quizzes = [
    {
        "questions": "Which function is used to take input in python ?",
        "Option": ["A.print()", "B.input()", "C.len()", "D.str()"],
        "Answer": "B"
    },
    {
        "questions": "Which python data structure stores values in key:value pair ?",
        "Option": ["A.List", "B.Tuple", "C.Dictionary", "D.String"],
        "Answer": "C"
    },
    {
        "questions": "Who invented python?",
        "Option": ["A.James Gosling", "B.Dennis Ritchie", "C.Guido van Rossum", "D.Bill Gates"],
        "Answer": "C"
    },
    {
        "questions": "For printing thousands of records which concept is used in python?",
        "Option": ["A.list", "B.Tuple", "C.set", "D.LOOP"],
        "Answer": "D"
    },
    {
        "questions": "Which keyword is used to define function in python?",
        "Option": ["A.def", "B.numpy", "C.pandas", "D.function"],
        "Answer": "A"
    }
]
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
    total = len(Quizzes)
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
                if a and a.upper() == Quizzes[idx]["Answer"].upper():
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
    quiz = Quizzes[idx]
    return render_template(
        "Quiz_page.html",
        quiz=quiz,
        idx=idx,
        total=total,
        student_name=session.get("student_name", ""),
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
        return render_template('student_submitted.html', name=name, email=email, age=age, grade=grade)
    return render_template('student_form.html')

@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html", leaderboard=leaderboard_entries)

if __name__ == "__main__":
   app.run(debug=True)