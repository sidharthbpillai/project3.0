from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='event_manage'
        
    )
    return conn

@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        password = generate_password_hash(request.form['password'])
        phone = request.form['phone']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, contact, password, phone) VALUES (%s, %s, %s, %s, %s)', 
                       (name, email, contact, password, phone))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM events ORDER BY date DESC LIMIT 10')
    events = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', events=events)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM events WHERE id = %s', (event_id,))
    event = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('event_detail.html', event=event)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        phone = request.form['phone']
        cursor.execute('UPDATE users SET name = %s, email = %s, contact = %s, phone = %s WHERE id = %s',
                       (name, email, contact, phone, user_id))
        conn.commit()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('user_profile.html', user=user)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        location = request.form['location']
        description = request.form['description']
        created_by = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO events (title, date, location, description, created_by) VALUES (%s, %s, %s, %s, %s)', 
                       (title, date, location, description, created_by))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    return render_template('create_event.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM events')
    events = cursor.fetchall()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', events=events, users=users)

@app.route('/delete_event/<int:event_id>')
def delete_event(event_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id = %s', (event_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/favicon.ico')
def favicon():
    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
