from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import pymysql
import bcrypt
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.urandom(24)

load_dotenv()

def get_db_connection():
    try:
        return pymysql.connect(
            host=os.getenv('DB_HOST, localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Nitn3lav3al0cin'),
            database=os.getenv('DB_NAME', 'todousers'),
            port=int(os.getenv('DB_PORT', 3306))
        )
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/')
def index():
    if 'user_email' in session:
        email = session['user_email']
        connection = get_db_connection()
        if connection is None:
            return "Database connection error", 500

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE user_email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                    cursor.execute("SELECT id, content, checked FROM tasks WHERE user_id = %s", (user_id,))
                    tasks = cursor.fetchall()
                else:
                    tasks = []
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return "Database query error", 500
        finally:
            connection.close()

        return render_template('index.html', tasks=tasks)
    else:
        return redirect(url_for('signup'))

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        data_content = request.form.get('toDoItem', '')
        checked = 'checked' in request.form
        email = session.get('user_email')
        connection = get_db_connection()
        if connection is None:
            return "Database connection error", 500

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE user_email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                    sql = "INSERT INTO tasks (content, checked, user_id) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (data_content, int(checked), user_id))
                    connection.commit()
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return "Database insert error", 500
        finally:
            connection.close()

    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit(task_id):
    content = request.json.get('content')
    connection = get_db_connection()
    if connection is None:
        return jsonify(success=False, error="Database connection error"), 500

    try:
        with connection.cursor() as cursor:
            sql = "UPDATE tasks SET content = %s WHERE id = %s"
            cursor.execute(sql, (content, task_id))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return jsonify(success=False, error="Database update error"), 500
    finally:
        connection.close()
    
    return jsonify(success=True)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify(success=False, error="Database connection error"), 500

    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM tasks WHERE id = %s"
            cursor.execute(sql, (task_id,))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return jsonify(success=False, error="Database delete error"), 500
    finally:
        connection.close()
    
    return jsonify(success=True)

@app.route('/update/<int:task_id>', methods=['POST'])
def update(task_id):
    is_completed = request.json.get('checked',False)
    connection = get_db_connection()
    if connection is None:
        return jsonify(success=False, error="Database connection error"), 500

    try:
        with connection.cursor() as cursor:
            sql = "UPDATE tasks SET checked = %s WHERE id = %s"
            cursor.execute(sql, (int(is_completed), task_id))
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return jsonify(success=False, error="Database update error"), 500
    finally:
        connection.close()
    
    return jsonify(success=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
        except KeyError as e:
            return f"Missing form field: {e.args[0]}", 400

        connection = get_db_connection()
        if connection is None:
            return "Database connection error", 500

        try:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM users WHERE user_email = %s"
                cursor.execute(sql, (email,))
                count = cursor.fetchone()[0]
        except pymysql.MySQLError as e:
            print(f"Database query error (checking existing user_email): {e}")
            return "Database query error", 500
        finally:
            connection.close()

        if count > 0:
            return jsonify({'error': "Email is already registered. Please use another email."}), 400
            
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = get_db_connection()
        if connection is None:
            return "Database connection error", 500

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (user_name, user_email, user_password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, email, password_hash.decode('utf-8')))
                connection.commit()
        except pymysql.MySQLError as e:
            print(f"Database insert error: {e}")  # Logging the specific error
            return "Database insert error", 500
        finally:
            connection.close()

        session['user_email'] = email
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
        except KeyError as e:
            return f"Missing form field: {e.args[0]}", 400

        connection = get_db_connection()
        if connection is None:
            return "Database connection error", 500

        try:
            with connection.cursor() as cursor:
                sql = "SELECT user_password FROM users WHERE user_email = %s"
                cursor.execute(sql, (email,))
                result = cursor.fetchone()
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return "Database query error", 500
        finally:
            connection.close()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            session['user_email'] = email
            return redirect(url_for('index'))
        else:
            return "Invalid email or password."

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)


