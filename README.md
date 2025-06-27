Job Portal App


This is a Flask-based Job Portal Web Application designed to connect job seekers with employers. It provides functionalities for users to register, log in, post job listings, search for jobs, and apply, with an administrative panel for overall management.

Table of Contents
Features

User Roles

Tech Stack

Project Structure

Setup Instructions

Usage

Database Schema

Future Enhancements

License

Features
User Authentication: Secure registration, login, and logout for different user roles.

Job Listings: Browse available job listings on the homepage with search and filter capabilities.

Job Posting: Employers can post new job openings with detailed information (title, description, salary, location, company, category).

Job Application: Job seekers can view job details and apply for positions.

User Dashboards: Personalized dashboards for job seekers and employers to manage their respective activities.

Admin Panel: A dedicated administrative dashboard to manage all users and job listings on the platform, including viewing all applications.

User Roles
The application supports three distinct user roles:

Job Seeker:

Register and log in.

Search and filter job listings.

View detailed job descriptions.

Apply for jobs.

View their submitted applications on their dashboard.

Employer:

Register and log in.

Post new job listings.

Manage (view) their posted jobs on their dashboard.

View applications received for their jobs and update application statuses.

Admin:

Log in with special administrative credentials.

Access a central dashboard to view overall statistics (total users, jobs, applications).

Manage (view and delete) user accounts.

Manage (view and delete) all job listings.

View all job applications across the platform.

Tech Stack
Backend: Python (Flask)

Frontend: HTML5, CSS3, Bootstrap 5

Database: SQLite3

Password Hashing: Werkzeug Security

Project Structure
job-portal-app/
├── app.py                  # Main Flask application logic, routes, and views
├── database.py             # Script to initialize the SQLite database and tables
├── requirements.txt        # List of Python dependencies
├── README.md               # Project documentation (this file)
├── static/
│   └── css/
│       └── style.css       # Custom CSS for styling
└── templates/
    ├── base.html           # Base template for consistent navigation and footer
    ├── index.html          # Homepage displaying job listings and search filters
    ├── login.html          # User login form
    ├── register.html       # User registration form
    ├── post_job.html       # Employer form to post a new job
    ├── job_detail.html     # Page to display detailed job information
    ├── apply_job.html      # (Conceptual) Application confirmation page
    ├── dashboard.html      # User-specific dashboard (Job Seeker/Employer)
    ├── admin_dashboard.html# Admin overview dashboard
    ├── manage_users.html   # Admin page to manage user accounts
    ├── manage_jobs.html    # Admin page to manage job listings
    └── manage_applications.html # Admin page to view all applications

Setup Instructions
Follow these steps to get the Job Portal App up and running on your local machine.

1. Clone the Repository (or create project files)
If you have cloned the project from GitHub, navigate into the directory. If you are setting up manually, create a directory named job-portal-app and place all the provided source code files within it, maintaining the specified folder structure.

git clone https://github.com/your-username/Job-Portal-App.git # Replace with your repo URL
cd Job-Portal-App

2. Create a Python Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other Python projects.

python -m venv venv

3. Activate the Virtual Environment
On Windows (Command Prompt/PowerShell):

.\venv\Scripts\activate

On Windows (Git Bash/MINGW64):

source venv/Scripts/activate

On macOS/Linux:

source venv/bin/activate

4. Install Dependencies
With your virtual environment activated, install the required Python packages using pip:

pip install -r requirements.txt

5. Initialize the Database
Run the database.py script to create the necessary SQLite database file (job_portal.db) and set up all the required tables. This script also creates an initial Admin user.

python database.py

You should see a confirmation message in your terminal.

Default Admin Credentials:

Username: admin

Password: adminpass

6. Run the Flask Application
After the database is initialized, you can start the Flask development server:

flask run

7. Access the Application
Open your web browser and navigate to the address shown in your terminal, typically:

http://127.0.0.1:5000/

Usage
Homepage: Browse available job listings. Use the search bar and filters to narrow down results.

Register: Click "Register" in the navigation bar to create a new account. Choose your role (Job Seeker or Employer).

Login: Use your registered credentials to log in.

Job Seekers:

After logging in, you can view job details and apply for jobs.

Access your dashboard to see a list of jobs you've applied for and their current status.

Employers:

After logging in, click "Post a Job" to add a new listing.

Your dashboard will show your posted jobs and any applications you've received, allowing you to update their status.

Admin:

Log in using the default admin credentials (admin/adminpass).

Access the Admin Dashboard to manage users, jobs, and view all applications across the platform.

Database Schema
The SQLite database job_portal.db contains the following tables:

users: Stores user information.

id (INTEGER PRIMARY KEY AUTOINCREMENT)

username (TEXT UNIQUE NOT NULL)

password_hash (TEXT NOT NULL)

role (TEXT NOT NULL - 'job_seeker', 'employer', 'admin')

jobs: Stores job listing details.

id (INTEGER PRIMARY KEY AUTOINCREMENT)

employer_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES users(id))

title (TEXT NOT NULL)

description (TEXT NOT NULL)

salary (TEXT)

location (TEXT)

category (TEXT)

company (TEXT)

applications: Stores job application details.

id (INTEGER PRIMARY KEY AUTOINCREMENT)

job_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES jobs(id))

seeker_id (INTEGER NOT NULL, FOREIGN KEY REFERENCES users(id))

application_date (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

status (TEXT DEFAULT 'pending' - 'pending', 'accepted', 'rejected')

Future Enhancements
Job Editing: Allow employers to edit their posted job listings.

User Profile Management: Enable users to update their profile information and change passwords.

"Forgot Password" Functionality: Implement a password reset mechanism.

Application Withdrawal: Allow job seekers to withdraw their submitted applications.

Enhanced Search Filters: Add more advanced filtering and sorting options for job search.

API Integration: Optionally fetch job listings from external job board APIs.

Notifications: Implement email or in-app notifications for new applications, status updates, etc.
