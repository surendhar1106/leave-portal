from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3


app = Flask(__name__)

app.secret_key = 'y'


# Initializing Data Base
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS leave_requests (
                id INTEGER PRIMARY KEY,
                leave_type TEXT,
                from_date TEXT,
                to_date TEXT,
                from_time TEXT,
                to_time TEXT,
                reason TEXT,
                status TEXT  DEFAULT 'Pending'
            )
        ''')

    with sqlite3.connect('database.db') as conn:
        conn.execute(''' 
            CREATE TABLE IF NOT EXISTS student_info (
                     id INTEGER PRIMARY KEY,
                     name TEXT,
                     student_id TEXT,
                     password TEXT
                     year TEXT
                     )
        ''')


    with sqlite3.connect('database.db') as conn:
        conn.execute(''' 
            CREATE TABLE IF NOT EXISTS faculty_info (
                     id INTEGER PRIMARY KEY,
                     name TEXT,
                     faculty_id TEXT,
                     password TEXT
                     )
''')


init_db()

#landing page
@app.route('/')
def index():
    session['slogged_in'] = False
    session['flogged_in'] = False
    return render_template('student_login.html')


#Register page
@app.route('/register_page')
def register_page():
    return render_template('Register.html')


#Register Route
@app.route('/register' , methods=['POST'])
def register():
        name = request.form['name']
        student_id = request.form['student_id']
        password = request.form['password']
        year = request.form['year']
        role = request.form.get('role')

        if role == 'student':
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                # Check if student_id already exists
                cursor.execute('SELECT * FROM student_info WHERE student_id = ?', (student_id,))
                if cursor.fetchone():
                    return render_template('Register.html', error='Student ID already registered.')

                # Insert new student
                cursor.execute('INSERT INTO student_info (name, student_id, password,year) VALUES (?, ?, ? , ?)', 
                            (name, student_id, password,year))
                conn.commit()
                return render_template('Register.html', message='Registration successful! Please login.')
        
        elif role == 'staff':
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                # Check if faculty_id already exists
                cursor.execute('SELECT * FROM faculty_info WHERE faculty_id = ?', (student_id,))
                if cursor.fetchone():
                    return render_template('Register.html', error='Faculty ID already registered.')

                # Insert new faculty
                cursor.execute('INSERT INTO faculty_info (name, faculty_id, password) VALUES (?, ?, ?)', 
                            (name, student_id, password))
                conn.commit()
                return render_template('Register.html', message='Registration successful! Please login.')
            
        else:
            return render_template('Register.html', error='Please choose a role')
        

#login check and route student page
@app.route('/slogin', methods=['POST'])
def login():

    username = request.form.get('studentid')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    stored_username = 'user'
    stored_password = '123789'

    print(username , password,user_type)

    if user_type == 'student':
    
        if username == stored_username and password == stored_password:
            session['slogged_in'] = True
            return redirect(url_for('student_dashboard'))
        
        else:
            if username != stored_username and password != stored_password:
                return render_template('student_login.html', username_placeholder = "Invalid ID", password_placeholder="Wrong password", error=True)
            
            elif username != stored_username and password == stored_password:
                return render_template('student_login.html', username_placeholder = "Invalid ID", error=True)
            
            elif username == stored_username and password != stored_password:
                return render_template('student_login.html', password_placeholder="Wrong password", error=True)
     
    elif user_type == 'staff':
        return redirect(url_for('staff_login_page'))
    

#student dashboard route
@app.route('/student_dashboard')
def student_dashboard():
    print(session['slogged_in'])
    if 'slogged_in' in session and session['slogged_in']:
        with sqlite3.connect('database.db') as conn:
            info = conn.execute('SELECT * FROM student_info').fetchall()
            rows = conn.execute('SELECT * FROM leave_requests').fetchall()
            print(rows)
            print(info)
        return render_template('student_dashboard.html', records=rows, student_info=info)
    else:
        return redirect(url_for('index'))
    

#staff login page route
@app.route('/staff_login_page')
def staff_login_page():
    return render_template('staff_login_page.html')


#staff dashboard route
@app.route('/faculty_dashboard')
def faculty_dashboard():
    print(session['flogged_in'])
    if 'flogged_in' in session and session['flogged_in']:
        return render_template('faculty_dashboard.html')
    else:
        return redirect(url_for('staff_login_page'))


#staff login and rerouting to student login
@app.route('/srr', methods=['POST'])
def rr_student():

    username = request.form.get('staffid')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    stored_username = 'staff'
    stored_password = '123'

    print(username , password,user_type)

    if user_type == 'staff':
    
        if username == stored_username and password == stored_password:
            session['flogged_in'] = True
            return redirect(url_for('faculty_dashboard'))
        
        else:
            return "invalid credentials, please try again.", 401
     
    elif user_type == 'student':
        return redirect(url_for('index'))


#leave apply page route
@app.route('/leave_page')
def leave_page():
    return render_template('leave_apply.html')


#leave submit 
@app.route('/submit_leave', methods=['POST'])
def submit_leave():
    
    leave_type = request.form.get('leave_type')
    from_date = request.form.get('from-date')
    to_date = request.form.get('to-date')
    from_time = request.form.get('from-time')
    to_time = request.form.get('to-time')
    reason = request.form.get('reason')
    status = 'Pending'
    print(leave_type,from_date,to_date,from_time,to_time,reason)

    with sqlite3.connect('database.db') as conn:
         conn.execute('''
                INSERT INTO leave_requests (leave_type, from_date, to_date, from_time, to_time, reason, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (leave_type, from_date, to_date, from_time, to_time, reason,status)) 

    return redirect(url_for('student_dashboard'))

#main check
if __name__ == '__main__':
    app.run(debug=True)

