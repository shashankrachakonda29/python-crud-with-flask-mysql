import sys
from flask import Flask, render_template, request, redirect, url_for
# from flask import *
from dbconnection import db

# Add your database connection path here if necessary
# sys.path.append('D:/CourseVideos/AWSPythonPractice/PythonNotes/Pythonproject/dbconnection')

cur_obj, connection = db.connection_Database()

# Create table if it doesn't exist
cur_obj.execute('CREATE TABLE IF NOT EXISTS branches3 (Roll_NO INT PRIMARY KEY, Fname VARCHAR(20), Lname VARCHAR(20), branch VARCHAR(20));')


app = Flask(__name__)


@app.route('/products')
def products():
    return "This page for products"

@app.route('/admin')
def admin():
    return 'This is admin'

@app.route('/student')
def student():
    return 'This is student'

@app.route('/staff')
def staff():
    return 'This is staff'

@app.route('/user/<name>')
def user(name):
    if name == 'admin':
        return redirect(url_for('admin'))
    elif name == 'student':
        return redirect(url_for('student'))
    elif name == 'staff':
        return redirect(url_for('staff'))
    else:
        return "User not found"

def Userdata(roll_no, fname, lname, branch):
    try:
        sql = "INSERT INTO students (Roll_NO, Fname, Lname, branch) VALUES (%s, %s, %s, %s)"
        val = (roll_no, fname, lname, branch)
        cur_obj.execute(sql, val)
        connection.commit()
        return True  # Indicate success
    except Exception as e:
        print(f"Error: {e}")
        return False  # Indicate failure

@app.route('/', methods=['GET', 'POST'])
def form():
    print('Request method:', request.method)
      # Fetch all student records on initial page load
    students = get_all_students()
    if request.method == "POST":
        roll_no = request.form['roll_no']
        fname = request.form['fname']
        lname = request.form['lname']
        branch = request.form['branch']
        if Userdata(roll_no, fname, lname, branch):
            students = get_all_students()  # Re-fetch records after insertion
            return render_template('index2.html', students=students, success=True)
        else:
            return render_template('error.html')  # Render an error template
    return render_template('index2.html', students=students)
def get_all_students():
    try:
        cur_obj.execute("SELECT Roll_NO, Fname, Lname, branch FROM students")
        return cur_obj.fetchall() # Returns a list of tuples
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

if __name__ == '__main__':
    app.run(debug=True, port=4500)
cur_obj.close()

