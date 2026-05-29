# Welcome to Python! - Student Management Starter
print("Welcome to Student Management System")
print("=" * 40)

# Variables - Store information
student_name = "John"
student_age = 20
student_id = "S001"

# Display student info
print(f"Name: {student_name}")
print(f"Age: {student_age}")
print(f"Student ID: {student_id}")

# List - Store multiple students
students = ["John", "Jane", "Bob", "Alice"]
print(f"\nTotal students: {len(students)}")

# Loop - Repeat for each student
print("\nStudent List:")
for student in students:
    print(f"  - {student}")

# If/Else - Make decisions
if student_age >= 18:
    print(f"\n{student_name} is an adult")
else:
    print(f"\n{student_name} is a minor")