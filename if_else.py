Questions=["2+2 ?",
           "capital of India ?",
           "How many days are in there week ?",
           "How many months are there in a year ?",
           "How many hours are there in a day ?",
           "What is the color of sky ?"]
Answers=["4",
         "New Delhi",
            "7",
            "12",
            "24",
            "Blue"]
def quiz():
     score=0
     for i in range(len(Questions)):
       print(f"\nQuestion {i+1}: {Questions[i]}")
       user_input=input("Your answer : ")
       if user_input==Answers[i]:
            print("Correct")
            score+=1
       else:
            print("Wrong")
     print(f"\nYour final score is: {score}/{len(Questions)}")

quiz()