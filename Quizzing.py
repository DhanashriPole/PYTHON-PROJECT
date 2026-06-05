from flask import Flask, render_template, request, redirect
app = Flask(__name__, template_folder='Temoplate')

student = {
    "Name": "",
    "Score": 0,
    "Attempted questions": 0
}

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
    if request.method == "POST":
        name = request.form.get("student_name", "Guest").strip() or "Guest"
        score = 0
        attempted = 0
        for idx, quiz in enumerate(Quizzes, start=1):
            answer = request.form.get(f"q{idx}", "")
            if answer:
                attempted += 1
                if answer.upper() == quiz["Answer"].upper():
                    score += 1
        update_leaderboard(name, score)
        percentage = round(score / len(Quizzes) * 100, 1)
        return render_template(
            "quiz_result.html",
            name=name,
            score=score,
            attempted=attempted,
            total=len(Quizzes),
            percentage=percentage,
            leaderboard=leaderboard_entries,
        )
    return render_template("Quiz_page.html", quizzes=Quizzes)

@app.route("/Information")
def Study_quiz_hub():
     return render_template("Study_quiz_hub.html")

leaderboard_entries = [
    {"rank": 1, "name": "Aarti", "score": 5},
    {"rank": 2, "name": "Kaveri", "score": 4},
    {"rank": 3, "name": "Divya", "score": 4},
    {"rank": 4, "name": "Rohini", "score": 3},
    {"rank": 5, "name": "Sowmya", "score": 2}
]

@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html", leaderboard=leaderboard_entries)

if __name__ == "__main__":
   app.run(debug=True)