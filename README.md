# Job Tracker Application

## COP4751 Course Project

### Project Overview

Job Tracker is a web application designed to help users organize their job search. The application allows users to manage companies, job listings, applications, and professional contacts in one place. It also includes a dashboard for viewing summary statistics and a Job Match feature for comparing user skills with job requirements.

### Technologies Used

- **Python** — application logic
- **Flask** — web application framework
- **MySQL** — relational database
- **HTML** — page structure
- **CSS** — styling and responsive layout

### Features

**Dashboard**
- Displays summary counts for companies, jobs, applications, and contacts.

**Company Management**
- Add, view, edit, and delete company records.

**Job Management**
- View job listings and manage job information.
- Store job details, salary ranges, job types, posting dates, and requirements.

**Application Management**
- Track job applications and their statuses.
- Store application dates, interview dates, response dates, and notes.

**Contact Management**
- Store professional contact information, including names, email addresses, phone numbers, job titles, and LinkedIn URLs.

**Job Match**
- Compare skills entered by the user against the skills required by saved jobs.
- Display skill-match percentages and matching skills.

**Navigation and Styling**
- Provides shared navigation across application pages.
- Uses a common layout and stylesheet for a consistent interface.

### Project Structure

```text
job_tracker/
├── app.py
├── database.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── companies.html
│   ├── jobs.html
│   ├── applications.html
│   ├── contacts.html
│   └── job_match.html
└── static/
    └── style.css
```

### Prerequisites

- Python 3
- MySQL Server
- A MySQL database configured for the application
- pip, the Python package installer

### Installation and Setup

1. Clone the project repository from GitHub.
2. Open a terminal in the project directory.
3. Create and activate a Python virtual environment if desired.
4. Install the Python dependencies listed in `requirements.txt`.
5. Create the project database in MySQL and configure the required tables and relationships.
6. Update `database.py` with the appropriate local MySQL connection settings.
7. Start the Flask application:

   ```bash
   python app.py
   ```

8. Open the application in a browser at:

   `http://127.0.0.1:5001`

### Database

The application uses MySQL to store companies, jobs, applications, and contacts. Related records use database relationships to associate jobs with companies and applications with jobs. Job requirements can be stored as JSON data to support skill matching.

### Testing

The following features should be tested before submission:

- Dashboard totals display correctly.
- Company records can be created, edited, and deleted.
- Job listings can be viewed and managed.
- Applications can be created, updated, and deleted.
- Contacts can be created, edited, and deleted.
- Job Match returns results when skills are entered.
- Navigation links and page styling work correctly.
- Database connections and relationships work as expected.

### Author

Student: Sonali Mohammed 

Course: COP4751

Project: Job Tracker Application
