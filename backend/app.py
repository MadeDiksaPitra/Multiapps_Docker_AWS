from flask import Flask, request, jsonify, session
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
            host='db'
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/admin/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO admin (username, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            cur.close()
            conn.close()
            return '', 201
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            print(f"Error executing query: {e}")
            return jsonify({"error": "Database error"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/admin/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('SELECT id FROM admin WHERE username = %s AND password = %s', (username, password))
        admin = cur.fetchone()
        cur.close()
        conn.close()

        if admin:
            session['admin_id'] = admin[0]
            return '', 204
        else:
            return jsonify({"error": "Invalid credentials"}), 403
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/admin/logout', methods=['POST'])
def logout():
    session.pop('admin_id', None)
    return '', 204

@app.route('/api/admin/status', methods=['GET'])
def check_login_status():
    if 'admin_id' in session:
        return '', 204
    else:
        return jsonify({"error": "Unauthorized"}), 403

@app.route('/api/books', methods=['GET'])
@login_required
def get_books():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM books;')
        books = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(books)
    else:
        return "Could not connect to database", 500

@app.route('/api/books', methods=['POST'])
@login_required
def add_book():
    new_book = request.get_json()
    title = new_book.get('title')
    author = new_book.get('author')

    if not title or not author:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO books (title, author) VALUES (%s, %s) RETURNING id', (title, author))
            book_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            new_book['id'] = book_id
            return jsonify(new_book), 201
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            print(f"Error executing query: {e}")
            return jsonify({"error": "Database error"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/books/<int:id>', methods=['PUT'])
@login_required
def update_book(id):
    updated_book = request.get_json()
    title = updated_book.get('title')
    author = updated_book.get('author')

    if not title or not author:
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute('UPDATE books SET title = %s, author = %s WHERE id = %s', (title, author, id))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify(updated_book)
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            print(f"Error executing query: {e}")
            return jsonify({"error": "Database error"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

@app.route('/api/books/<int:id>', methods=['DELETE'])
@login_required
def delete_book(id):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute('DELETE FROM books WHERE id = %s', (id,))
            conn.commit()
            cur.close()
            conn.close()
            return '', 204
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            print(f"Error executing query: {e}")
            return jsonify({"error": "Database error"}), 500
    else:
        return jsonify({"error": "Database connection failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
