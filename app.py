from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
  return '<h1>Welcome to my project!</h1>' 
@app.route('/about')
def about():
    return '<h1>About Us</h1><p>This is a simple Flask application.</p>'
@app.route('/students')
def students():
    return '<h1>Student Directory</h1><p>Here you can find information about our students.</p>'
if __name__ == '__main__':
    app.run(debug=True)