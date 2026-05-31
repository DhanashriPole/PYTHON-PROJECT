Name=input("enter your name:");
java_marks=int(input("enter your java marks:"));
python_marks=int(input("enter your python marks: "));
micrpcessor_marks=int(input("enter your microprocessor marks: "));
Chemistry_marks=int(input("enter your chemistry marks: "));
physics_marks=int(input("enter your physics marks: "));
total_marks=java_marks+python_marks+micrpcessor_marks+Chemistry_marks+physics_marks;
percentage=(total_marks/500)*100;
print("total marks=",total_marks);
print("percentage=",percentage);
if percentage>=90:
    print("grade=A");
elif percentage>=80:
    print("grade=B");
elif percentage>=70:
    print("grade=C");
elif percentage>=60:
    print("grade=D");
else:
    print("grade=F");

