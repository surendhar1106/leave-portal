from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.secret_key = 'y'

st_id = ''
f_id = ''

@app.route('/approve/<int:leave_id>', methods=['POST'])
def approve_leave(leave_id):
    if not session.get('flogged_in'):
        return redirect(url_for('staff_login_page'))
    
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            UPDATE leave_requests 
            SET status = 'Approved' 
            WHERE id = ?
        ''', (leave_id,))
    
    return redirect(url_for('faculty_dashboard'))

@app.route('/reject/<int:leave_id>', methods=['POST'])
def reject_leave(leave_id):
    if not session.get('flogged_in'):
        return redirect(url_for('staff_login_page'))
    
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            UPDATE leave_requests 
            SET status = 'Rejected' 
            WHERE id = ?
        ''', (leave_id,))
    
    return redirect(url_for('faculty_dashboard'))

def extract_number(student_id):
    try:
        # Remove all non-digit characters
        return int(''.join(filter(str.isdigit, student_id)))
    except ValueError:
        return 0  # Fallback for invalid IDs

def assign_faculty(student_id):
    numeric_id = extract_number(student_id)
    faculty_num = ((numeric_id - 1) // 20) + 1
    return f"f{faculty_num}"

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
                status TEXT  DEFAULT 'Pending',
                st_id TEXT
            )
        ''')
        with sqlite3.connect('database.db') as conn:
            conn.execute('''
               CREATE TABLE IF NOT EXISTS faculty_assignments (
                    faculty_id TEXT,
                    student_id TEXT,
                    PRIMARY KEY (faculty_id, student_id)
                 )
                ''')

    with sqlite3.connect('database.db') as conn:
        conn.execute(''' 
    CREATE TABLE IF NOT EXISTS student_info (
        id INTEGER PRIMARY KEY,
        name TEXT,
        student_id TEXT,
        password TEXT,
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
        role = request.form.get('role')

        if role == 'student':
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                # Check if student_id already exists
                cursor.execute('SELECT * FROM student_info WHERE student_id = ?', (student_id,))
                if cursor.fetchone():
                    return render_template('Register.html', error='Student ID already registered.')

                # Insert new student
                cursor.execute('INSERT INTO student_info (name, student_id, password) VALUES (?, ?, ?)', 
                            (name, student_id, password))
                conn.commit()
            faculty_ = assign_faculty(student_id)
            print(faculty_)
            with sqlite3.connect('database.db') as conn:
                conn.execute('''
                    INSERT INTO faculty_assignments (faculty_id, student_id)
                    VALUES (?, ?)
                ''', (faculty_, student_id))
                print("inserted sucessfuly")

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

    if user_type == 'student':
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor() 
            cursor.execute("SELECT * FROM student_info WHERE student_id = ?", (username,))
            user = cursor.fetchone()

            if user:
                stored_password = user[3]
                hashed_password = generate_password_hash(stored_password)
                if check_password_hash(hashed_password, password):
                    session['slogged_in'] = True
                    global st_id
                    st_id = username
                    return redirect(url_for('student_dashboard'))
                else:
                    return render_template('student_login.html', er = "wrong password")
            else:
                return render_template('student_login.html', er="no user found!")
     
    elif user_type == 'staff':
        return redirect(url_for('staff_login_page'))
    

#student dashboard route
@app.route('/student_dashboard')
def student_dashboard():
    print(session['slogged_in'])
    if 'slogged_in' in session and session['slogged_in']:
        with sqlite3.connect('database.db') as conn:
            global sinfo
            print(st_id)
            try:
                sinfo = conn.execute("SELECT * FROM student_info WHERE student_id = ?", (st_id,)).fetchone()
                print(sinfo)
                if sinfo is None:
                    print('sinfo is none')
                    render_template('student_dashboard.html', student_info = None, er = "sinfo is none!")
            except:
                print('no user found')
                return render_template('student_dashboard.html', student_info = None, er = "no user info found !")
            try:
                rows = conn.execute("SELECT * FROM leave_requests WHERE st_id = ?", (st_id,)).fetchall()
            except:
                print('no record found')
                return render_template('student_dashboard.html',student_info = None, er = "no records found!")

            return render_template('student_dashboard.html',student_info = sinfo, records=rows)
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
         with sqlite3.connect('database.db') as conn:
            conn.row_factory = sqlite3.Row
            global finfo
            print(f_id)
            try:
                finfo = conn.execute("SELECT * FROM faculty_info WHERE faculty_id = ?", (f_id,)).fetchone()
                print(finfo)
                if finfo is None:
                    print('finfo is none')
                    render_template('faculty_dashboard.html', f_info = None, er = "finfo is none!")
            except:
                print('no user found')
                return render_template('faculty_dashboard.html', f_info = None, er = "no user info found !")
            try:
                 with sqlite3.connect('database.db') as conn:
                    conn.row_factory = sqlite3.Row  # Enable column name access
                    leave_requests = conn.execute('''
            SELECT l.*, s.name as student_name
            FROM leave_requests l
            JOIN student_info s ON l.st_id = s.student_id
            JOIN faculty_assignments fa ON s.student_id = fa.student_id
            WHERE fa.faculty_id = ?
            ORDER BY l.status, l.from_date DESC
        ''', (f_id,)).fetchall()
                    print(leave_requests)
                 return render_template('faculty_dashboard.html', requests=leave_requests,f_info = finfo)
            except Exception as e:
                print('no record found because : ',e)
                return render_template('faculty_dashboard.html',requests=[],f_info = None, er = "no records found!")

    else:
        return redirect(url_for('staff_login_page'))


#staff login and rerouting to student login
@app.route('/srr', methods=['POST'])
def rr_student():

    username = request.form.get('staffid')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    print(username , password,user_type)

    if user_type == 'staff':
         with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor() 
            cursor.execute("SELECT * FROM faculty_info WHERE faculty_id = ?", (username,))
            user = cursor.fetchone()

            if user:
                stored_password = user[3]
                hashed_password = generate_password_hash(stored_password)
                if check_password_hash(hashed_password, password):
                    session['flogged_in'] = True
                    global f_id
                    f_id = username
                    return redirect(url_for('faculty_dashboard'))
                else:
                    return render_template('staff_login_page.html', er = "wrong password")
            else:
                return render_template('staff_login_page.html', er="no user found!")
     
       
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
                INSERT INTO leave_requests (leave_type, from_date, to_date, from_time, to_time, reason, status,st_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (leave_type, from_date, to_date, from_time, to_time, reason,status,st_id)) 

    return redirect(url_for('student_dashboard'))

#main check
if __name__ == '__main__':
    app.run(debug=True)

