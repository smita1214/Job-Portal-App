import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here_please_change_this_to_a_strong_random_string'
DATABASE = 'job_portal.db'

# --- Database Helper Functions ---
def get_db():
    """Establishes a database connection or returns the existing one."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # This allows accessing columns by name
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Context Processor to inject current_year into all templates ---
@app.context_processor
def inject_current_year():
    """Injects the current year into all templates."""
    return {'current_year': datetime.datetime.now().year}

# --- Authentication Decorators ---
def login_required(f):
    """Decorator to ensure a user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    """Decorator to ensure a user has a specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role_name:
                flash(f'You do not have permission to access this page. {role_name} role required.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Routes ---

@app.route('/')
def index():
    """Homepage: Displays a list of available jobs."""
    db = get_db()
    cursor = db.cursor()
    search_query = request.args.get('search', '')
    location_filter = request.args.get('location', '')
    category_filter = request.args.get('category', '')
    company_filter = request.args.get('company', '')

    query = "SELECT j.*, u.username as employer_username FROM jobs j JOIN users u ON j.employer_id = u.id WHERE 1=1"
    params = []

    if search_query:
        query += " AND (j.title LIKE ? OR j.description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
    if location_filter:
        query += " AND j.location LIKE ?"
        params.append(f'%{location_filter}%')
    if category_filter:
        query += " AND j.category LIKE ?"
        params.append(f'%{category_filter}%')
    if company_filter:
        query += " AND j.company LIKE ?"
        params.append(f'%{company_filter}%')

    query += " ORDER BY j.id DESC"
    jobs = cursor.execute(query, params).fetchall()

    return render_template('index.html', jobs=jobs,
                           search_query=search_query,
                           location_filter=location_filter,
                           category_filter=category_filter,
                           company_filter=company_filter)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role'] # 'job_seeker' or 'employer'

        db = get_db()
        cursor = db.cursor()

        # Check if username already exists
        existing_user = cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing_user:
            flash('Username already taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, password_hash, role))
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            flash(f'An error occurred during registration: {e}', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome, {user["username"]}! You have been logged in as a {user["role"]}.', 'success')

            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logs out the current user."""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User-specific dashboard for job seekers and employers."""
    db = get_db()
    cursor = db.cursor()
    user_id = session['user_id']
    user_role = session['role']

    jobs_posted = []
    applications_made = []
    applications_received = []

    if user_role == 'employer':
        # Get jobs posted by this employer
        jobs_posted = cursor.execute("SELECT * FROM jobs WHERE employer_id = ? ORDER BY id DESC", (user_id,)).fetchall()
        # Get applications for jobs posted by this employer
        applications_received = cursor.execute('''
            SELECT a.*, j.title AS job_title, u.username AS seeker_username
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN users u ON a.seeker_id = u.id
            WHERE j.employer_id = ? ORDER BY a.application_date DESC
        ''', (user_id,)).fetchall()
    elif user_role == 'job_seeker':
        # Get applications made by this job seeker
        applications_made = cursor.execute('''
            SELECT a.*, j.title AS job_title, j.company, j.location
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.seeker_id = ? ORDER BY a.application_date DESC
        ''', (user_id,)).fetchall()

    return render_template('dashboard.html',
                           user_role=user_role,
                           jobs_posted=jobs_posted,
                           applications_made=applications_made,
                           applications_received=applications_received)

@app.route('/post_job', methods=['GET', 'POST'])
@login_required
@role_required('employer')
def post_job():
    """Employer page to post a new job."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        salary = request.form['salary']
        location = request.form['location']
        category = request.form['category']
        company = request.form['company']
        employer_id = session['user_id']

        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO jobs (employer_id, title, description, salary, location, category, company) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (employer_id, title, description, salary, location, category, company))
            db.commit()
            flash('Job posted successfully!', 'success')
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f'An error occurred while posting the job: {e}', 'danger')
            return redirect(url_for('post_job'))
    return render_template('post_job.html')

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Displays details of a specific job."""
    db = get_db()
    cursor = db.cursor()
    job = cursor.execute("SELECT j.*, u.username AS employer_username FROM jobs j JOIN users u ON j.employer_id = u.id WHERE j.id = ?", (job_id,)).fetchone()

    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('index'))

    # Check if the current user has already applied for this job
    has_applied = False
    if 'user_id' in session and session['role'] == 'job_seeker':
        seeker_id = session['user_id']
        application = cursor.execute("SELECT id FROM applications WHERE job_id = ? AND seeker_id = ?", (job_id, seeker_id)).fetchone()
        if application:
            has_applied = True

    return render_template('job_detail.html', job=job, has_applied=has_applied)

@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
@role_required('job_seeker')
def apply_job(job_id):
    """Allows a job seeker to apply for a job."""
    db = get_db()
    cursor = db.cursor()
    seeker_id = session['user_id']

    # Check if job exists
    job = cursor.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('index'))

    # Check if already applied
    existing_application = cursor.execute("SELECT id FROM applications WHERE job_id = ? AND seeker_id = ?", (job_id, seeker_id)).fetchone()
    if existing_application:
        flash('You have already applied for this job.', 'warning')
        return redirect(url_for('job_detail', job_id=job_id))

    try:
        cursor.execute("INSERT INTO applications (job_id, seeker_id) VALUES (?, ?)",
                       (job_id, seeker_id))
        db.commit()
        flash('Application submitted successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'An error occurred during application: {e}', 'danger')

    return redirect(url_for('job_detail', job_id=job_id))

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard."""
    db = get_db()
    cursor = db.cursor()

    total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_jobs = cursor.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    total_applications = cursor.execute("SELECT COUNT(*) FROM applications").fetchone()[0]

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_jobs=total_jobs,
                           total_applications=total_applications)

@app.route('/admin/manage_users')
@login_required
@role_required('admin')
def manage_users():
    """Admin page to manage users."""
    db = get_db()
    cursor = db.cursor()
    users = cursor.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    return render_template('manage_users.html', users=users)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Admin action to delete a user."""
    db = get_db()
    cursor = db.cursor()
    try:
        # Delete related applications and jobs first to maintain referential integrity
        cursor.execute("DELETE FROM applications WHERE seeker_id = ?", (user_id,))
        cursor.execute("DELETE FROM jobs WHERE employer_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        flash('User deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Error deleting user: {e}', 'danger')
    return redirect(url_for('manage_users'))

@app.route('/admin/manage_jobs')
@login_required
@role_required('admin')
def manage_jobs():
    """Admin page to manage job listings."""
    db = get_db()
    cursor = db.cursor()
    jobs = cursor.execute("SELECT j.*, u.username as employer_username FROM jobs j JOIN users u ON j.employer_id = u.id ORDER BY j.id DESC").fetchall()
    return render_template('manage_jobs.html', jobs=jobs)

@app.route('/admin/delete_job/<int:job_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_job(job_id):
    """Admin action to delete a job."""
    db = get_db()
    cursor = db.cursor()
    try:
        # Delete related applications first
        cursor.execute("DELETE FROM applications WHERE job_id = ?", (job_id,))
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        db.commit()
        flash('Job deleted successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Error deleting job: {e}', 'danger')
    return redirect(url_for('manage_jobs'))

# NEW ROUTE FOR ADMIN TO MANAGE ALL APPLICATIONS
@app.route('/admin/manage_applications')
@login_required
@role_required('admin')
def manage_applications():
    """Admin page to manage all job applications."""
    db = get_db()
    cursor = db.cursor()
    applications = cursor.execute('''
        SELECT a.*, j.title AS job_title, j.company, u_seeker.username AS seeker_username, u_employer.username AS employer_username
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u_seeker ON a.seeker_id = u_seeker.id
        JOIN users u_employer ON j.employer_id = u_employer.id
        ORDER BY a.application_date DESC
    ''').fetchall()
    return render_template('manage_applications.html', applications=applications)

@app.route('/update_application_status/<int:application_id>', methods=['POST'])
@login_required
@role_required('employer') # Only employers can update application status
def update_application_status(application_id):
    """Allows an employer to update the status of an application."""
    db = get_db()
    cursor = db.cursor()
    new_status = request.form['status']
    employer_id = session['user_id']

    # Validate status
    if new_status not in ['pending', 'accepted', 'rejected']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Verify the application belongs to a job posted by this employer
        application = cursor.execute('''
            SELECT a.id, j.employer_id
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.id = ?
        ''', (application_id,)).fetchone()

        if application and application['employer_id'] == employer_id:
            cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, application_id))
            db.commit()
            flash(f'Application status updated to "{new_status}"!', 'success')
        else:
            flash('You are not authorized to update this application or application not found.', 'danger')
    except sqlite3.Error as e:
        flash(f'An error occurred: {e}', 'danger')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
