"""
Library Management System - Flask Backend
==========================================
Tech Stack: Python + Flask + MySQL
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import date, timedelta, datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'library-secret-key-2025')
app.jinja_env.globals.update(enumerate=enumerate)

# ─────────────────────────────────────────
# DATABASE CONFIG — update with your MySQL credentials
# ─────────────────────────────────────────
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'library_db'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '123456789'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def get_db():
    """Get MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def query_db(sql, params=(), fetchone=False, commit=False):
    """Execute a query and return results."""
    conn = get_db()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        if commit:
            conn.commit()
            return cursor.lastrowid
        result = cursor.fetchone() if fetchone else cursor.fetchall()
        return result
    except Error as e:
        print(f"Query error: {e}")
        if commit:
            conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

# ─────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = query_db('SELECT * FROM users WHERE email=%s AND is_active=1', (email,), fetchone=True)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        existing = query_db('SELECT id FROM users WHERE email=%s', (email,), fetchone=True)
        if existing:
            flash('Email already registered.', 'danger')
        else:
            hashed = generate_password_hash(password)
            query_db('INSERT INTO users (name, email, password, phone) VALUES (%s,%s,%s,%s)',
                     (name, email, hashed, phone), commit=True)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    total_books = query_db('SELECT COUNT(*) as c FROM books', fetchone=True)['c']
    total_users = query_db('SELECT COUNT(*) as c FROM users WHERE role="member"', fetchone=True)['c']
    active_borrows = query_db('SELECT COUNT(*) as c FROM reservations WHERE status IN ("borrowed","reserved")', fetchone=True)['c']
    overdue = query_db('SELECT COUNT(*) as c FROM reservations WHERE status="overdue"', fetchone=True)['c']
    recent_activity = query_db('''
        SELECT r.id, u.name as user_name, b.title as book_title, r.status, r.reserved_date, r.due_date
        FROM reservations r
        JOIN users u ON r.user_id=u.id
        JOIN books b ON r.book_id=b.id
        ORDER BY r.created_at DESC LIMIT 8
    ''')
    popular_books = query_db('''
        SELECT b.title, b.author, COUNT(r.id) as borrow_count
        FROM books b LEFT JOIN reservations r ON b.id=r.book_id
        GROUP BY b.id ORDER BY borrow_count DESC LIMIT 5
    ''')
    return render_template('dashboard.html',
        total_books=total_books, total_users=total_users,
        active_borrows=active_borrows, overdue=overdue,
        recent_activity=recent_activity, popular_books=popular_books)

# ─────────────────────────────────────────
# BOOKS
# ─────────────────────────────────────────
@app.route('/books')
@login_required
def books():
    search = request.args.get('q', '')
    genre = request.args.get('genre', '')
    if search:
        rows = query_db('''SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s
                           ORDER BY title''', (f'%{search}%', f'%{search}%', f'%{search}%'))
    elif genre:
        rows = query_db('SELECT * FROM books WHERE genre=%s ORDER BY title', (genre,))
    else:
        rows = query_db('SELECT * FROM books ORDER BY title')
    genres = query_db('SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL ORDER BY genre')
    return render_template('books.html', books=rows, genres=genres, search=search, selected_genre=genre)

@app.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip() or None
        genre = request.form.get('genre', '').strip()
        publisher = request.form.get('publisher', '').strip()
        year = request.form.get('year_published') or None
        copies = int(request.form.get('total_copies', 1))
        description = request.form.get('description', '').strip()
        query_db('''INSERT INTO books (title,author,isbn,genre,publisher,year_published,
                    total_copies,available_copies,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                 (title, author, isbn, genre, publisher, year, copies, copies, description), commit=True)
        flash(f'Book "{title}" added successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('book_form.html', book=None)

@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = query_db('SELECT * FROM books WHERE id=%s', (book_id,), fetchone=True)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip() or None
        genre = request.form.get('genre', '').strip()
        publisher = request.form.get('publisher', '').strip()
        year = request.form.get('year_published') or None
        copies = int(request.form.get('total_copies', 1))
        description = request.form.get('description', '').strip()
        diff = copies - book['total_copies']
        new_avail = max(0, book['available_copies'] + diff)
        query_db('''UPDATE books SET title=%s,author=%s,isbn=%s,genre=%s,publisher=%s,
                    year_published=%s,total_copies=%s,available_copies=%s,description=%s WHERE id=%s''',
                 (title, author, isbn, genre, publisher, year, copies, new_avail, description, book_id), commit=True)
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('book_form.html', book=book)

@app.route('/books/delete/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    book = query_db('SELECT title FROM books WHERE id=%s', (book_id,), fetchone=True)
    if book:
        query_db('DELETE FROM books WHERE id=%s', (book_id,), commit=True)
        flash(f'Book "{book["title"]}" deleted.', 'info')
    return redirect(url_for('books'))

# ─────────────────────────────────────────
# USERS (Admin only)
# ─────────────────────────────────────────
@app.route('/users')
@admin_required
def users():
    search = request.args.get('q', '')
    if search:
        rows = query_db('SELECT * FROM users WHERE name LIKE %s OR email LIKE %s ORDER BY name',
                        (f'%{search}%', f'%{search}%'))
    else:
        rows = query_db('SELECT * FROM users ORDER BY role DESC, name')
    return render_template('users.html', users=rows, search=search)

@app.route('/users/toggle/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user(user_id):
    user = query_db('SELECT name, is_active FROM users WHERE id=%s', (user_id,), fetchone=True)
    if user and user_id != session['user_id']:
        new_status = 0 if user['is_active'] else 1
        query_db('UPDATE users SET is_active=%s WHERE id=%s', (new_status, user_id), commit=True)
        status_text = 'activated' if new_status else 'deactivated'
        flash(f'User "{user["name"]}" {status_text}.', 'info')
    return redirect(url_for('users'))

@app.route('/users/promote/<int:user_id>', methods=['POST'])
@admin_required
def promote_user(user_id):
    user = query_db('SELECT name, role FROM users WHERE id=%s', (user_id,), fetchone=True)
    if user:
        new_role = 'member' if user['role'] == 'admin' else 'admin'
        query_db('UPDATE users SET role=%s WHERE id=%s', (new_role, user_id), commit=True)
        flash(f'"{user["name"]}" is now {new_role}.', 'success')
    return redirect(url_for('users'))

# ─────────────────────────────────────────
# RESERVATIONS
# ─────────────────────────────────────────
@app.route('/reservations')
@login_required
def reservations():
    if session['role'] == 'admin':
        rows = query_db('''
            SELECT r.*, u.name as user_name, b.title as book_title, b.author
            FROM reservations r JOIN users u ON r.user_id=u.id JOIN books b ON r.book_id=b.id
            ORDER BY r.created_at DESC
        ''')
    else:
        rows = query_db('''
            SELECT r.*, b.title as book_title, b.author
            FROM reservations r JOIN books b ON r.book_id=b.id
            WHERE r.user_id=%s ORDER BY r.created_at DESC
        ''', (session['user_id'],))
    return render_template('reservations.html', reservations=rows, today=date.today())

@app.route('/reserve/<int:book_id>', methods=['POST'])
@login_required
def reserve_book(book_id):
    book = query_db('SELECT * FROM books WHERE id=%s', (book_id,), fetchone=True)
    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('books'))
    if book['available_copies'] < 1:
        flash('No copies available right now.', 'warning')
        return redirect(url_for('books'))
    existing = query_db('''SELECT id FROM reservations WHERE user_id=%s AND book_id=%s AND status IN ("reserved","borrowed")''',
                        (session['user_id'], book_id), fetchone=True)
    if existing:
        flash('You already have this book reserved or borrowed.', 'warning')
        return redirect(url_for('books'))
    due_date = date.today() + timedelta(days=14)
    query_db('''INSERT INTO reservations (user_id, book_id, due_date, status) VALUES (%s,%s,%s,'reserved')''',
             (session['user_id'], book_id, due_date), commit=True)
    query_db('UPDATE books SET available_copies=available_copies-1 WHERE id=%s', (book_id,), commit=True)
    flash(f'"{book["title"]}" reserved! Due date: {due_date}.', 'success')
    return redirect(url_for('reservations'))

@app.route('/reservations/update/<int:res_id>', methods=['POST'])
@admin_required
def update_reservation(res_id):
    action = request.form.get('action')
    res = query_db('SELECT * FROM reservations WHERE id=%s', (res_id,), fetchone=True)
    if not res:
        flash('Reservation not found.', 'danger')
        return redirect(url_for('reservations'))
    if action == 'borrow' and res['status'] == 'reserved':
        query_db("UPDATE reservations SET status='borrowed' WHERE id=%s", (res_id,), commit=True)
        flash('Marked as borrowed.', 'success')
    elif action == 'return' and res['status'] in ('borrowed', 'overdue'):
        fine = 0.0
        if res['due_date'] and date.today() > res['due_date']:
            overdue_days = (date.today() - res['due_date']).days
            fine = overdue_days * 2.0
        query_db("UPDATE reservations SET status='returned', return_date=%s, fine_amount=%s WHERE id=%s",
                 (date.today(), fine, res_id), commit=True)
        query_db('UPDATE books SET available_copies=available_copies+1 WHERE id=%s', (res['book_id'],), commit=True)
        msg = f'Book returned. Fine: ₹{fine:.2f}' if fine > 0 else 'Book returned successfully.'
        flash(msg, 'success' if fine == 0 else 'warning')
    elif action == 'cancel' and res['status'] == 'reserved':
        query_db("UPDATE reservations SET status='cancelled' WHERE id=%s", (res_id,), commit=True)
        query_db('UPDATE books SET available_copies=available_copies+1 WHERE id=%s', (res['book_id'],), commit=True)
        flash('Reservation cancelled.', 'info')
    return redirect(url_for('reservations'))

# ─────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = query_db('SELECT * FROM users WHERE id=%s', (session['user_id'],), fetchone=True)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        new_password = request.form.get('new_password', '')
        if new_password:
            hashed = generate_password_hash(new_password)
            query_db('UPDATE users SET name=%s,phone=%s,address=%s,password=%s WHERE id=%s',
                     (name, phone, address, hashed, session['user_id']), commit=True)
        else:
            query_db('UPDATE users SET name=%s,phone=%s,address=%s WHERE id=%s',
                     (name, phone, address, session['user_id']), commit=True)
        session['name'] = name
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    my_history = query_db('''
        SELECT r.*, b.title as book_title, b.author FROM reservations r
        JOIN books b ON r.book_id=b.id WHERE r.user_id=%s ORDER BY r.created_at DESC
    ''', (session['user_id'],))
    return render_template('profile.html', user=user, history=my_history)

# ─────────────────────────────────────────
# API ENDPOINTS (JSON)
# ─────────────────────────────────────────
@app.route('/api/stats')
@login_required
def api_stats():
    stats = {
        'total_books': query_db('SELECT COUNT(*) as c FROM books', fetchone=True)['c'],
        'available_books': query_db('SELECT SUM(available_copies) as c FROM books', fetchone=True)['c'] or 0,
        'total_members': query_db('SELECT COUNT(*) as c FROM users WHERE role="member"', fetchone=True)['c'],
        'active_borrows': query_db('SELECT COUNT(*) as c FROM reservations WHERE status IN ("borrowed","reserved")', fetchone=True)['c'],
        'overdue': query_db('SELECT COUNT(*) as c FROM reservations WHERE status="overdue"', fetchone=True)['c'],
        'returned_today': query_db('SELECT COUNT(*) as c FROM reservations WHERE return_date=CURDATE()', fetchone=True)['c'],
    }
    return jsonify(stats)

@app.route('/api/overdue-check')
@admin_required
def overdue_check():
    """Mark borrowed books past due date as overdue."""
    count = query_db('''UPDATE reservations SET status='overdue'
                        WHERE status='borrowed' AND due_date < CURDATE()''', commit=True)
    return jsonify({'message': 'Overdue check complete', 'updated': count or 0})

# ─────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
