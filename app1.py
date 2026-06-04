from flask import Flask, render_template
app = Flask(__name__)

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
def home():
    return render_template('home.html')

@app.route("/Que")
def quiz():
     return render_template('quiz.html', quizzes=Quizzes)

@app.route("/about")
def about():
    return render_template('about.html')

if __name__=="__main__":
    app.run(debug=True)