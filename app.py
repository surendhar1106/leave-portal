from flask import Flask, render_template, request, redirect, url_for,session

app = Flask(__name__)

app.secret_key = 'y'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    # Dummy login (you can add logic later)
    username = request.form['username']
    password = request.form['password']

    stored_username = 'user'
    stored_password = '123789'

    if username == stored_username and password == stored_password:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    
    else:
        return "invalid credentials, please try again.", 401
    

@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session and session['logged_in']:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('index'))
    

@app.route('/submitrequest', methods=['POST'])
def submitrequest():
    reason = request.form['reason']
    from_date = request.form['from_date']
    to_date = request.form['to_date']

    print(f"reason:{reason},date:{from_date}:{to_date}")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
