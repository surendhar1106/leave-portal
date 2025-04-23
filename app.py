from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

app.secret_key = 'y'


#landing page
@app.route('/')
def index():
    session['logged_in'] = False
    return render_template('student_login.html')


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
            session['logged_in'] = True
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
    print(session['logged_in'])
    if 'logged_in' in session and session['logged_in']:
        return render_template('student_dashboard.html')
    else:
        return redirect(url_for('index'))
    

#staff login page route
@app.route('/staff_login_page')
def staff_login_page():
    return render_template('staff_login_page.html')


#staff dashboard route
@app.route('/faculty_dashboard')
def faculty_dashboard():
    return render_template('faculty_dashboard.html')


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
            session['logged_in'] = True
            return redirect(url_for('faculty_dashboard'))
        
        else:
            return "invalid credentials, please try again.", 401
     
    elif user_type == 'student':
        return redirect(url_for('index'))


#main check
if __name__ == '__main__':
    app.run(debug=True)
