from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector
import pymysql

app = Flask(__name__)
app.secret_key = 'Password'

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Baripada@123")
DB_NAME = os.getenv("DB_NAME", "user_database")

def get_db_conn():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    

def get_user(username):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s",(username,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and user['password'] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid Credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Password confirmation check
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            return render_template('signup.html', error="Username already exists!")

        # Insert new user into database
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))  # Redirect to login page after signup

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = get_user(session['user'])
        return render_template('dashboard.html', username=user['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)