import sys,os,webbrowser,hashlib
from flask import Flask, render_template, request, redirect,flash, url_for,session
# from flask import *
from dbconnection import db
import pandas as pd
from functools import wraps
import locale

locale.setlocale(locale.LC_ALL,'en-IN')
# Add your database connection path here if necessary
# sys.path.append('D:/CourseVideos/AWSPythonPractice/PythonNotes/Pythonproject/dbconnection')

cur_obj, connection = db.connection_Database()
# If the database connection fails, this code will raise an exception and stops the execution of the code.
if cur_obj is None and connection is None:
    raise Exception("Failed to connect to the database.")

# Create table if it doesn't exist
# cur_obj.execute('CREATE TABLE IF NOT EXISTS branches3 (Roll_NO INT PRIMARY KEY, Fname VARCHAR(20), Lname VARCHAR(20), branch VARCHAR(20));')

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret')
user_name=''

# ----------------------------    Authentication Decorator  Start-----------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:  # Check if the user is logged in
            flash('You need to log in first.', 'danger')
            return redirect('/')  # Redirect to login page
            # return redirect(url_for('login'))  # Redirect to login page
        return f(*args, **kwargs)
    return decorated_function
# ----------------------------    Authentication Decorator  End-----------------------



# ------------------------------ login Part Start -------------------------------------
@app.route('/')
def index():
    session.pop('user',None)
    return render_template('index.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        Name = request.form['name']
        Email = request.form['email']
        Passwd = request.form['passwd']

        cur_obj.execute('CREATE TABLE IF NOT EXISTS users (Name VARCHAR(20), Email VARCHAR(50), Password VARCHAR(128), role VARCHAR(20));')
        connection.commit()  # Commit the table creation
        try:
            # Create the users table if it doesn't exist

            # Check if the user already exists
            if Checkuserexists(Email):
                flash('User already exists. Please log in.', 'warning')
                return redirect(url_for('login'))  # Redirect to login or appropriate page

            # Hash the password for security
            hashed_passwd = hashlib.sha256(Passwd.encode()).hexdigest()
            print("62",hashed_passwd)

            # Insert the new user into the database
            sql = "INSERT INTO users (Name, Email, Password, role) VALUES (%s, %s, %s, %s)"
            val = (Name, Email, hashed_passwd, 'admin')  # Assuming default role is 'user'
            cur_obj.execute(sql, val)
            connection.commit()

            flash('Signup successful! You can now log in.', 'success')
            return redirect(url_for('login'))  # Redirect to login or welcome page

        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred during signup. Please try again.', 'danger')

    # return render_template('index.html')  # Render signup template for GET request
    return redirect('/')  # Render signup template for GET request

def Checkuserexists(email):
    # Implement logic to check if the user already exists in the database
    cur_obj.execute("SELECT * FROM users WHERE Email = %s", (email,))
    cur_obj.fetchone()
    return cur_obj.rowcount > 0 # Returns True if user exists

def Checkuseremailandpasswdexists(email,password):
    # Check if the email exists
    cur_obj.execute("SELECT 1 FROM users WHERE Email = %s", (email,))
    if cur_obj.fetchone() is not None:
         # Check's if the email  and password exists 
        cur_obj.execute("SELECT * FROM users WHERE Email = %s AND Password = %s", (email, password))
        user_data = cur_obj.fetchone()  # Fetch the user data
        if user_data is not None:
            return user_data  # Return the user data if credentials are correct
        else:
            flash("Incorrect password. Please try again.", "danger")
            return False
    else:
        flash("Email ID doesn't exist. Please try again or sign up.")
        return False
@app.route('/login',methods=["GET", "POST"])
def login():
    if request.method == "POST":
        Email = request.form['lemail']
        Passwd = request.form['lpasswd']
        hashed_input_password = hashlib.sha256(Passwd.encode()).hexdigest()
        print("106",hashed_input_password)
        user_info=Checkuseremailandpasswdexists(Email,hashed_input_password)
        if user_info == False:
            user_info=Checkuseremailandpasswdexists(Email,Passwd)
        if user_info:
            session['user'] = Email
            session['name'] = user_info[0]
            global user_name
            user_name= session.get('name')
            # return redirect(url_for('home'))
            return redirect('/home')
            # return render_template('home.html',name=user_info[0])
            # return redirect(url_for('dashboard'))
    return redirect('/home')
    # return render_template('index.html')
    # return redirect(url_for('index'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html',name=user_name)

@app.route('/logout')
def logout():
    session.pop('user',None)
    # return redirect(url_for('login'))
    # return redirect(url_for('index'))
    return redirect('/')
# ------------------------------ login Part End -------------------------------------






@app.route('/admin')
@login_required
def admin():
    return 'This is admin'

@app.route('/student')
@login_required
def student():
    return 'This is student'

@app.route('/staff')
@login_required
def staff():
    return 'This is staff'

@app.route('/user/<name>')
@login_required
def user(name):
    if name == 'admin':
        return redirect(url_for('admin'))
    elif name == 'student':
        return redirect(url_for('student'))
    elif name == 'staff':
        return redirect(url_for('staff'))
    elif name == 'product':
        return render_template('product.html')
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
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    print('Request method:', request.method)
    user_name = session.get('name')
      # Fetch all student records on initial page load
    students = get_all_students()
    if request.method == "POST":
        roll_no = request.form['roll_no']
        fname = request.form['fname']
        lname = request.form['lname']
        branch = request.form['branch']
        if Userdata(roll_no, fname, lname, branch):
            students = get_all_students()  # Re-fetch records after insertion
            return render_template('index2.html', students=students,name=user_name, success=True)
        else:
            return render_template('error.html')  # Render an error template
    return render_template('index2.html', students=students,name=user_name)
def get_all_students():
    try:
        cur_obj.execute("SELECT * FROM students")
        return cur_obj.fetchall() # Returns a list of tuples
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
@app.route('/editstudent/<int:id>', methods=['POST'])
def edit_student(id):
    # Get data from the form
    roll_no = request.form['roll_no']  # Assuming roll_no is the same as the ID
    fname = request.form['fname']
    lname = request.form['lname']
    branch = request.form['branch']

    # Update the student in the database
    cur_obj.execute("""
        UPDATE students SET Fname=%s, Lname=%s, branch=%s WHERE Roll_NO=%s
    """, (fname, lname, branch, roll_no))
    connection.commit()

    flash('Student updated successfully!', 'success')
    return redirect(url_for('dashboard'))  # Redirect to the main page or wherever you need


@app.route('/user/<int:id>', methods=['POST'])
def deletestudent(id):
    # SQL command to delete the student with the specified Roll_NO
    employeetbl_delete = f"DELETE FROM students WHERE Roll_NO={id}"
    try:
        # Execute the delete command
        cur_obj.execute(employeetbl_delete)
        connection.commit()  # Commit the transaction

        # flash('Student deleted successfully!', 'success')
        # Re-fetch updated records to display the latest student list
        students = get_all_students()  
        return render_template('index2.html', students=students, success=True)

    except Exception as e:
        # Print the error message to the console
        print(f"Error deleting data: {e}")
        # flash('An error occurred while deleting the student.', 'danger')
        # Optionally, you can render the template with an error message
        students = get_all_students()  # Re-fetch to show the existing records
        return render_template('index2.html', students=students, error=True)



# ------------------------- XLSX upload Start -----------------------------------
@app.route('/xlsxupload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        # Set uploads directory dynamically
        uploads_dir = os.path.join(app.instance_path, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        # Get the uploaded file
        file = request.files['xlsx_file']
        # if file.filename == '':
        try:
            if file and file.filename.endswith('.xlsx'):
                filename = file.filename
                file_path = os.path.join(uploads_dir, filename)
                file.save(file_path)
            else:
                raise ValueError('No file selected or invalid file format')
        except ValueError as e:
            return redirect(url_for('upload_file', message=str(e)))


        # Load the Excel file using pandas
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
        except FileNotFoundError:
            return redirect(url_for('upload_file', message='Error: File not found'))

        # Iterate over sheets and upload data
        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Prepare SQL statements
            columns = ', '.join(f"`{col}` {get_sql_type(dtype)}" for col, dtype in zip(df.columns, df.dtypes))
            placeholders = ', '.join(['%s'] * len(df.columns))
            # columns_int = ', '.join(f"`{col}`" for col in df.columns)

            try:
                cur_obj.execute(f"CREATE TABLE IF NOT EXISTS `{sheet_name}` ({columns});")

                # Execute bulk insert using parameterized queries

                sql = f"INSERT INTO `{sheet_name}` ({', '.join(f"`{col}`" for col in df.columns)}) VALUES ({placeholders})"
                # sql = f"INSERT INTO `{sheet_name}` ({columns_int}) VALUES ({placeholders})"
                list_data = df.values.tolist()
                cur_obj.executemany(sql, list_data)
                connection.commit()
                copy_html_file(sheet_name)


                print(f"Data from sheet '{sheet_name}' uploaded successfully!")
                redirect(url_for('dynamicfunc',pagename=sheet_name))
            except Exception as err:
                print(f"Error uploading sheet '{sheet_name}': {err}")

        return redirect(url_for('upload_file', message='File uploaded successfully'))

    return render_template('xlsxupload.html',name=user_name)

# @app.route('/emi',methods=['GET', 'POST'])
# def emi():
#     if request.method == "POST":
#         Total_item_amt=int(request.form['loan_amount'])
#         down_payment=int(request.form['down_payment'])
#         interest_rate=float(request.form['interest_rate'])
#         loan_tenure=int(request.form['loan_tenure'])
#         [Yaerly_distributed,BreakUp]=emiCalculator(Total_item_amt,down_payment,interest_rate,loan_tenure)
#         Formdetails={"Total_item_amt":Total_item_amt,"down_payment":down_payment,"interest_rate":interest_rate,"loan_tenure":loan_tenure}
#         return render_template('emi.html',Yaerly=Yaerly_distributed,BreakUp=BreakUp,Formdetails=Formdetails)
#     return render_template('emi.html')

# def emiCalculator(Total_item_amt,down_payment,rate,Tenure):
#     # Calculate loan amount (assuming no down payment for simplicity)
#     Yearly_Amount=[]
#     loan_amt=Total_item_amt - down_payment
#     Loan_amt = loan_amt
#     months = Tenure * 12  # Total number of months
#     intrst = round((rate / 12) / 100,7)  # Monthly interest rate

#     # Store total principal repaid for yearly calculations
#     total_principal_repaid = 0
#     # Store total Interest  for yearly calculations
#     total_interest_repaid = 0
    

#     # Loop through each year to calculate interest and principal
#     for year in range(1, Tenure + 1):
#         interest_amt_year = 0  # Initialize yearly interest amount
#         principal_repaid_year = 0  # Initialize yearly principal repaid
#         remaining_principal = Loan_amt  # Start with the full loan amount
    
#         # Calculate EMI using the formula
#         Emi = (Loan_amt * intrst * (1 + intrst) ** months) / ((1 + intrst) ** months - 1)
#         if year == 1:
#             first_month=Emi
#         for month in range(1, 12 + 1):
#             months-=1
            
#             # Calculate interest for the current month
#             Interest_for_Month = remaining_principal * intrst
            
#             # Calculate principal component for the current month
#             Principal_Component = Emi - Interest_for_Month
            
#             # Update the remaining principal
#             remaining_principal -= Principal_Component
            
#             # Accumulate interest and principal for the year
#             interest_amt_year += Interest_for_Month
#             principal_repaid_year += Principal_Component

#         # After all months, print the results for the year
#         Loan_amt=Closing_balance = remaining_principal
#         Yearly_Amount.append({
#             "Year": year,
#             'Opening Balance': round(Total_item_amt - total_principal_repaid),
#             "Interest Paid During Year": round(interest_amt_year),
#             "Principal Repaid During Year": round(principal_repaid_year),
#             "Closing Balance": round(Closing_balance)
#         })
#         # Update total principal repaid for the next year
#         total_principal_repaid += principal_repaid_year
#         total_interest_repaid += interest_amt_year
#     payable_amt=total_principal_repaid+total_interest_repaid
#     return [Yearly_Amount,{"total_interest_repaid":int(total_interest_repaid),"total_principal_repaid":round(total_principal_repaid),"payable_amt":int(payable_amt),"first_month":int(first_month)}]

# -------------------------  EMI Calculation Start  ------------------------------------------

@app.route('/emi', methods=['GET', 'POST'])
@login_required
def emi():
    if request.method == "POST":
        # Get form data
        print('in')
        Total_item_amt = int(request.form['loan_amount'])
        down_payment = int(request.form['down_payment'])
        interest_rate = float(request.form['interest_rate'])
        loan_tenure = int(request.form['loan_tenure'])

        # Perform the EMI calculation
        Yearly_Amount, BreakUp = emimonthlyCalculator(Total_item_amt, down_payment, interest_rate, loan_tenure)

        # Store results in session
        session['Yearly'] = Yearly_Amount
        session['BreakUp'] = BreakUp
        session['Formdetails'] = {
            "Total_item_amt": Total_item_amt,
            "down_payment": down_payment,
            "interest_rate": interest_rate,
            "loan_tenure": loan_tenure
        }

        return redirect('/emi/results')

    return render_template('emi.html',name=user_name)

@app.route('/emi/results')
def emi_results():
    # Retrieve results from session
    Yearly_Amount = session.get('Yearly', [])
    BreakUp = session.get('BreakUp', {})
    Formdetails = session.get('Formdetails', {})

    # Clear session data after retrieval
    session.pop('Yearly', None)
    session.pop('BreakUp', None)
    session.pop('Formdetails', None)

    return render_template('emi.html', Yearly=Yearly_Amount, BreakUp=BreakUp, Formdetails=Formdetails,name=user_name)

def emimonthlyCalculator(item_amt, down_payment, rate, Tenure):
    Yearly_Amount = []
   
    Total_item_amt = item_amt - down_payment
    Loan_amt = Total_item_amt
    months = Tenure * 12  # Total number of months
    intrst = round((rate / 12) / 100, 7)  # Monthly interest rate

    total_principal_repaid = 0
    total_interest_repaid = 0

    for year in range(1, Tenure + 1):
        Monthly_Amount=[]
        interest_amt_year = 0
        principal_repaid_year = 0
        remaining_principal = Loan_amt

        # Calculate EMI
        Emi = (Loan_amt * intrst * (1 + intrst) ** months) / ((1 + intrst) ** months - 1)
        if year == 1:
            first_month = Emi
            total_fin_amt=first_month*months
            no_of_days=Tenure*365
            daily=round(total_fin_amt/no_of_days,4)
        for month in range(12):
            months -= 1
            
            # Calculate interest for the current month
            Interest_for_Month = remaining_principal * intrst
            
            # Calculate principal component for the current month
            Principal_Component = Emi - Interest_for_Month
            
            # Monthly_Amount.append({"Month":month+1,"principal_Amount":locale.format_string('%.1f', remaining_principal, grouping=True),"Interest_for_Month":round(Interest_for_Month,1),"principal_amt_month":round(Principal_Component,1),"Total_amt_Month":round(Interest_for_Month+Principal_Component,1),"Remaining_Principal":int(remaining_principal-Principal_Component)})
            Monthly_Amount.append({
                "Month": month + 1,
                "principal_Amount": locale.format_string('%.1f', remaining_principal, grouping=True),
                "Interest_for_Month": locale.format_string('%.1f', Interest_for_Month, grouping=True),
                "principal_amt_month": locale.format_string('%.1f', Principal_Component, grouping=True),
                "Total_amt_Month": locale.format_string('%.1f', Interest_for_Month + Principal_Component, grouping=True),
                "Remaining_Principal": locale.format_string('%d', int(remaining_principal - Principal_Component), grouping=True)
            })
            # Update the remaining principal
            remaining_principal -= Principal_Component
            
            # Accumulate interest and principal for the year
            interest_amt_year += Interest_for_Month
            principal_repaid_year += Principal_Component

        Loan_amt=Closing_balance = remaining_principal
        Yearly_Amount.append({
            "Year": year,
            'Opening Balance': locale.format_string('%d',round(Total_item_amt - total_principal_repaid), grouping=True),
            "Interest Paid During Year": locale.format_string('%d',round(interest_amt_year), grouping=True),
            "Principal Repaid During Year": locale.format_string('%d',round(principal_repaid_year), grouping=True),
            "Closing Balance": locale.format_string('%d',round(Closing_balance), grouping=True),
            "Monthly Amount":Monthly_Amount
        })
        total_principal_repaid += principal_repaid_year
        total_interest_repaid += interest_amt_year

    payable_amt = total_principal_repaid + total_interest_repaid
    return Yearly_Amount, {"total_interest_repaid": locale.format_string('%d',int(total_interest_repaid), grouping=True), 
                             "total_principal_repaid": locale.format_string('%d',round(total_principal_repaid), grouping=True), 
                             "payable_amt": locale.format_string('%d',int(payable_amt), grouping=True), 
                             "first_month": locale.format_string('%d',int(first_month), grouping=True),
                             "daily_amount":locale.format_string('%.4f',daily, grouping=True),"Tenure":Tenure,"Total_months":Tenure*12,"No_days":locale.format_string('%d',no_of_days, grouping=True)}

# -------------------------    EMI Calculation End   -------------------------------------------

# ---------------------------- IT Tax Start ----------------------------------------------------
@app.route("/tax",methods=['GET','POST'])
@login_required
def tax():
    if request.method == "POST":
        Salary=int(request.form['annual_salary'])
        tax_rates = [
            (300001, 700000, 5),
            (700001, 1000000, 10),
            (1000001, 1200000, 15),
            (1200001, 1500000, 20),
            (1500001, float('inf'), 30)
        ]
        tax = 0
        rate = 0  # Default rate

        if Salary > 300000:
            for lower, upper, r in tax_rates:
                if lower <= Salary <= upper:
                    rate = r
                    tax = (Salary * rate) / 100
                    break

        fin_salary = Salary - tax
        monthly_salary = fin_salary / 12
        monthly_tax = tax / 12
        session['incometax']={
            "Annual_Package":[locale.format_string("%d",Salary,grouping=True),Salary],
            "Annual_tax":locale.format_string("%d",tax,grouping=True),
            "tax_rate":locale.format_string("%d",rate,grouping=True),
            "Monthly_Salary":locale.format_string("%d",monthly_salary,grouping=True),
            "Monthly_tax":locale.format_string("%d",monthly_tax,grouping=True),
            "Final_Salary":locale.format_string("%d",fin_salary,grouping=True)
        }
        return redirect("/tax/details")
    return render_template('incometax.html',name=user_name)
@app.route('/tax/details')
def tax_details():
    Salary_tax=session.get('incometax',{})

    session.pop('incometax',None)

    return render_template('incometax.html',Salary=Salary_tax,name=user_name)

# ---------------------------- IT Tax End  ----------------------------------------------------


# Function to map DataFrame dtypes to SQL types
def get_sql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_string_dtype(dtype):
        return 'VARCHAR(255)'
    # Add more mappings as needed
    else:
        return 'TEXT'  # Default type

# ------------------------- XLSX upload End -------------------------------------



# --------------------------- Dummy Data Test Start------------------------------------------------
@app.route('/dynamicfunc/<pagename>')
def dynamicfunc(pagename):
#    f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'pythontestdb' AND TABLE_NAME = 'students'"
    cur_obj.execute("SELECT Database()")
    current_db = cur_obj.fetchone()
    cur_obj.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{current_db[0]}' AND TABLE_NAME = '{pagename}'")
    col_names = [column[0] for column in cur_obj.fetchall()]
    cur_obj.execute(f"SELECT * FROM `{current_db[0]}`.`{pagename}`")
    rows = cur_obj.fetchall()
    return render_template(f'{pagename}.html',colnames=col_names,rows=rows,name=user_name)

def move_html_file(pagename):
    old_location = './pages/blank.html'
    new_location = f'./templates/{pagename}.html'
    try:
        # Ensure the new directory exists
        new_dir = os.path.dirname(new_location)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        # Move the file
        os.rename(old_location, new_location)
        print(f"Moved {old_location} to {new_location}")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
def copy_html_file(pagename):
    old_location = './pages/blank.html'
    new_location = f'./templates/{pagename}.html'
    try:
        # Ensure the new directory exists
        os.makedirs(os.path.dirname(new_location), exist_ok=True)

        # Open the old file for reading and the new file for writing
        with open(old_location, 'r') as old_file:
            content = old_file.read()

        with open(new_location, 'w') as new_file:
            new_file.write(content)

        print(f"Copied {old_location} to {new_location}")

    except Exception as e:
        print(f"Error: {e}")


# --------------------------- Dummy Data Test End------------------------------------------------
@app.route('/Createpage')
def Createpage():
    cur_obj.execute('CREATE TABLE IF NOT EXISTS Pages (id MEDIUMINT NOT NULL AUTO_INCREMENT, Pagename VARCHAR(20),Tablename VARCHAR(20), Icon VARCHAR(20),PRIMARY KEY (id))')




if __name__ == '__main__':
    app.run(debug=True, port=4800)
cur_obj.close()

