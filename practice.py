names = ['disha', 'sneha', 'priya', 'suman', 'sneha']
scores = [85, 90, 78, 92, 88]
grades = ['A', 'A+', 'B', 'A+', 'A']
for i in range(5):
    def get_status(i):
        return f"name: {names[i]}, score: {scores[i]}, grade: {grades[i]}"
    print(get_status(i))