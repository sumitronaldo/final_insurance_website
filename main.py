from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector
import pymysql
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET')

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

db = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = db.cursor()

def get_db_conn():
    retries = 10
    while retries > 0:
        try:
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("✅ Connected to MySQL")
            return conn
        except pymysql.err.OperationalError as e:
            print(f"❌ Database connection failed: {e}")
            retries -= 1
            time.sleep(3)

    raise Exception("Could not connect to MySQL after multiple attempts.")

db = get_db_conn()
cursor = db.cursor()

cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

def init_db():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        ) 
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.select_db(DB_NAME)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            dob DATE NOT NULL,
            username VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and table initialized successfully.")
    except pymysql.MySQLError as err:
        print(f"Error initializing database: {err}")

init_db()
#def create_user(username, password):
#    conn = get_db_conn()
#    cursor = conn.cursor()
#    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
#    conn.commit()
#    conn.close()

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

       
        cursor.execute("SELECT username, dob FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = user[0]  
            session['dob'] = user[1]   
            flash("Login successful!", "success")
            return redirect(url_for('dashboard')) 
        else:
            flash("Invalid username or password!", "error")

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        dob = request.form['dob']
        confirm_password = request.form.get('confirm_password')

        
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")
        
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            return render_template('signup.html', error="Username already exists!")
        
        cursor.execute("INSERT INTO users (name, dob, username, password) VALUES (%s, %s, %s, %s)", (name, dob, username, password))
        db.commit()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login')) 

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'], dob=session['dob'])
    flash("Please login first !!")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!!","info")
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')


if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
