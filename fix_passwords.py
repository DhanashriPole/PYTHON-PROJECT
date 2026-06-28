import sqlite3
from werkzeug.security import generate_password_hash

# Connect to your quiz.db
conn = sqlite3.connect("quiz.db")

# Default password (students बाद में change कर सकते हैं)
default_password = "default123"
hashed_pw = generate_password_hash(default_password)

# Update all NULL passwords
conn.execute("UPDATE students SET password=? WHERE password IS NULL", (hashed_pw,))
conn.commit()
conn.close()

print("All NULL passwords updated with hashed default.")
