from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
        return redirect(url_for('dashboard'))
    
    else:
        return "invalid credentials, please try again.", 401
    

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
