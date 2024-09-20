from flask import Flask, render_template, request, redirect, url_for, session, jsonify,send_from_directory
import pymysql
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='Nitn3lav3al0cin',
        database='todousers'
    )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/')
def index():
    if 'email' in session:
        email = session['email']

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                    cursor.execute("SELECT id, task_content, is_completed FROM tasks WHERE user_id = %s", (user_id,))
                    tasks = cursor.fetchall()
                else:
                    tasks = []
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

        email = session.get('email')
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                result = cursor.fetchone()
                if result:
                    user_id = result[0]
                    sql = "INSERT INTO tasks (task_content, is_completed, user_id) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (data_content, int(checked), user_id))
                    connection.commit()
        finally:
            connection.close()

    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['POST'])
def edit(task_id):
    content = request.json.get('task_content')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE tasks SET task_content = %s WHERE id = %s"
            cursor.execute(sql, (content, task_id))
            connection.commit()
    finally:
        connection.close()
    
    return jsonify(success=True)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM tasks WHERE id = %s"
            cursor.execute(sql, (task_id,))
            connection.commit()
    finally:
        connection.close()
    
    return jsonify(success=True)

@app.route('/update/<int:task_id>', methods=['POST'])
def update(task_id):
    is_completed = request.json.get('is_completed')
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE tasks SET is_completed = %s WHERE id = %s"
            cursor.execute(sql, (int(is_completed), task_id))
            connection.commit()
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
        try:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                count = cursor.fetchone()[0]
        finally:
            connection.close()

        if count > 0:
            return jsonify({'error': "Email is already registered. Please use another email."}), 400
            
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, email, password_hash.decode('utf-8')))
                connection.commit()
        finally:
            connection.close()

        session['email'] = email
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
        try:
            with connection.cursor() as cursor:
                sql = "SELECT hashed_password FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                result = cursor.fetchone()
        finally:
            connection.close()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            session['email'] = email
            return redirect(url_for('index'))
        else:
            return "Invalid email or password."

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False) 


