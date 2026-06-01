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


def start_quiz():
    score = 0
    attempted = 0
    for quiz in Quizzes:
        print("\n" + quiz["questions"])
        for option in quiz["Option"]:
            print(option)
        answer = input("Enter your answer (A/B/C/D): ").strip().upper()
        attempted += 1
        if answer == quiz["Answer"].upper():
            print("Correct!")
            score += 1
        else:
            print("Wrong!")
    student["Score"] = score
    student["Attempted questions"] = attempted
    print("\nStudent name:", student["Name"])
    print("Score:", student["Score"], "/", len(Quizzes))
    print("Attempted questions:", student["Attempted questions"])


def search_record():
    keyword = input("Enter keyword: ")
    for quiz in Quizzes:
        if keyword.lower() in quiz["questions"].lower():
            print("\nQuestion:", quiz["questions"])
            print("Answer:", quiz["Answer"])
            return
    print("Question not found!")


if __name__ == "__main__":
    while True:
        print("\n==========STUDY QUIZ HUB===========")
        print("1. Start quiz")
        print("2. Search question")
        print("3. View student record")
        print("4. Set student name")
        print("5. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            start_quiz()
        elif choice == "2":
            search_record()
        elif choice == "3":
            print("\nName:", student["Name"])
            print("Score:", student["Score"])
            print("Attempted questions:", student["Attempted questions"])
        elif choice == "4":
            student["Name"] = input("Enter your name: ").strip()
        elif choice == "5":
            print("Thank you!")
            break
        else:
            print("Invalid choice")
