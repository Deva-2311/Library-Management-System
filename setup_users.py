"""
setup_users.py — Run this ONCE after importing schema.sql
to set correct hashed passwords for demo users.
"""
import mysql.connector
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    'host': 'localhost',
    'database': 'library_db',
    'user': 'root',
    'password': '123456789',   # ← Update this
}

users = [
    ('admin@library.com', 'admin123'),
    ('arjun@email.com',   'member123'),
    ('priya@email.com',   'member123'),
    ('ravi@email.com',    'member123'),
]

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

for email, raw_pw in users:
    hashed = generate_password_hash(raw_pw)
    cursor.execute('UPDATE users SET password=%s WHERE email=%s', (hashed, email))
    print(f'✅  Updated password for {email}')

conn.commit()
cursor.close()
conn.close()
print('\nDone! You can now login with the demo credentials.')
