import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'job_portal.db'

def init_db():
    """Initializes the database by creating tables and an admin user."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('job_seeker', 'employer', 'admin'))
        )
    ''')

    # Create jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            salary TEXT,
            location TEXT,
            category TEXT,
            company TEXT,
            FOREIGN KEY (employer_id) REFERENCES users (id)
        )
    ''')

    # Create applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            seeker_id INTEGER NOT NULL,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (seeker_id) REFERENCES users (id)
        )
    ''')

    # Insert admin user if not exists
    admin_username = 'admin'
    admin_password_hash = generate_password_hash('adminpass')
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       (admin_username, admin_password_hash, 'admin'))
        conn.commit()
        print(f"Admin user '{admin_username}' created successfully.")
    except sqlite3.IntegrityError:
        print(f"Admin user '{admin_username}' already exists.")

    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized and admin user created (if not exists).")