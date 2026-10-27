
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection

app = Flask(__name__)
app.secret_key = "job-tracker-development-key"


@app.route("/")
def dashboard():
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed. Check your MySQL settings.", 500

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM companies")
    companies_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM jobs")
    jobs_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM applications")
    applications_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM contacts")
    contacts_count = cursor.fetchone()["total"]
    
    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        companies_count=companies_count,
        jobs_count=jobs_count,
        applications_count=applications_count,
        contacts_count=contacts_count
    )


@app.route("/companies")
def companies():
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM companies ORDER BY company_id DESC")
    company_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "companies.html",
        companies=company_list,
        edit_company=None
    )


@app.route("/companies/add", methods=["POST"])
def add_company():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        flash("Company name is required.")
        return redirect(url_for("companies"))

    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO companies
        (company_name, industry, website, city, state, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        company_name,
        request.form.get("industry") or None,
        request.form.get("website") or None,
        request.form.get("city") or None,
        request.form.get("state") or None,
        request.form.get("notes") or None
    ))

    connection.commit()
    cursor.close()
    connection.close()

    flash("Company added successfully!")
    return redirect(url_for("companies"))


@app.route("/companies/edit/<int:company_id>", methods=["GET", "POST"])
def edit_company(company_id):
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()

        if not company_name:
            cursor.close()
            connection.close()
            flash("Company name is required.")
            return redirect(url_for("edit_company", company_id=company_id))

        cursor.execute("""
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                website = %s,
                city = %s,
                state = %s,
                notes = %s
            WHERE company_id = %s
        """, (
            company_name,
            request.form.get("industry") or None,
            request.form.get("website") or None,
            request.form.get("city") or None,
            request.form.get("state") or None,
            request.form.get("notes") or None,
            company_id
        ))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Company updated successfully!")
        return redirect(url_for("companies"))

    cursor.execute(
        "SELECT * FROM companies WHERE company_id = %s",
        (company_id,)
    )
    company = cursor.fetchone()

    cursor.close()
    connection.close()

    if company is None:
        return "Company not found.", 404

    # Reuse companies.html; no extra template needed.
    cursor_connection = get_db_connection()
    list_cursor = cursor_connection.cursor(dictionary=True)
    list_cursor.execute(
        "SELECT * FROM companies ORDER BY company_id DESC"
    )
    company_list = list_cursor.fetchall()
    list_cursor.close()
    cursor_connection.close()

    return render_template(
        "companies.html",
        companies=company_list,
        edit_company=company
    )


@app.route("/companies/delete/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM companies WHERE company_id = %s",
        (company_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    flash("Company deleted successfully!")
    return redirect(url_for("companies"))

    
@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed. Check your MySQL settings.", 500

    cursor = connection.cursor(dictionary=True)
    edit_job_id = request.args.get("edit", type=int)

    if request.method == "POST" and request.form.get("action") == "edit":
        job_id = request.form.get("job_id", type=int)

        cursor.execute("""
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_description = %s,
                salary_min = %s,
                salary_max = %s,
                job_type = %s,
                posting_url = %s,
                date_posted = %s,
                is_active = %s
            WHERE job_id = %s
        """, (
            request.form["company_id"],
            request.form["job_title"].strip(),
            request.form.get("job_description") or None,
            request.form.get("salary_min") or None,
            request.form.get("salary_max") or None,
            request.form.get("job_type") or None,
            request.form.get("posting_url") or None,
            request.form.get("date_posted") or None,
            request.form.get("is_active", "1"),
            job_id
        ))

        connection.commit()
        cursor.close()
        connection.close()
        flash("Job updated successfully!")
        return redirect(url_for("jobs"))

    cursor.execute("""
        SELECT
            j.job_id, j.company_id, j.job_title,
            j.job_description, j.salary_min, j.salary_max,
            j.job_type, j.posting_url, j.date_posted,
            j.is_active, j.requirements, c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.job_id DESC
    """)
    jobs_list = cursor.fetchall()

    job_to_edit = None
    if edit_job_id is not None:
        cursor.execute(
            "SELECT * FROM jobs WHERE job_id = %s",
            (edit_job_id,)
        )
        job_to_edit = cursor.fetchone()

    cursor.execute("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name
    """)
    companies_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "jobs.html",
        jobs=jobs_list,
        edit_job=job_to_edit,
        companies=companies_list
    )

@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed. Check your MySQL settings.", 500

    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        company_id = request.form["company_id"]
        job_title = request.form["job_title"]
        job_type = request.form.get("job_type") or None
        salary_min = request.form.get("salary_min") or None
        salary_max = request.form.get("salary_max") or None
        posting_url = request.form.get("posting_url") or None
        date_posted = request.form.get("date_posted") or None
        job_description = request.form.get("job_description") or None

        cursor.execute("""
            INSERT INTO jobs (
                company_id,
                job_title,
                job_type,
                salary_min,
                salary_max,
                posting_url,
                date_posted,
                job_description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            company_id,
            job_title,
            job_type,
            salary_min,
            salary_max,
            posting_url,
            date_posted,
            job_description
        ))

        connection.commit()
        cursor.close()
        connection.close()

        flash("Job added successfully!", "success")
        return redirect(url_for("jobs"))

    cursor.execute("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name
    """)
    companies_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "job_form.html",
        companies=companies_list
    )
@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM jobs WHERE job_id = %s",
        (job_id,)
    )

    deleted = cursor.rowcount
    connection.commit()
    cursor.close()
    connection.close()

    if deleted:
        flash("Job deleted successfully!")
    else:
        flash("Job not found.")

    return redirect(url_for("jobs"))

@app.route("/applications", methods=["GET", "POST"])
def applications():
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            cursor.execute("""
                INSERT INTO applications (
                    job_id, application_date, status,
                    resume_version, cover_letter_sent,
                    response_date, interview_date, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form["job_id"],
                request.form.get("application_date"),
                request.form.get("status") or "Applied",
                request.form.get("resume_version") or None,
                1 if request.form.get("cover_letter_sent") else 0,
                request.form.get("response_date") or None,
                request.form.get("interview_date") or None,
                request.form.get("notes") or None
            ))

            connection.commit()
            cursor.close()
            connection.close()
            flash("Application added successfully!")
            return redirect(url_for("applications"))

        elif action == "delete":
            application_id = request.form.get("application_id", type=int)

            cursor.execute(
                "DELETE FROM applications WHERE application_id = %s",
                (application_id,)
            )

            connection.commit()
            cursor.close()
            connection.close()
            flash("Application deleted successfully!")
            return redirect(url_for("applications"))

        elif action == "update":
            application_id = request.form.get("application_id", type=int)

            cursor.execute("""
                UPDATE applications
                SET status = %s,
                    response_date = %s,
                    interview_date = %s,
                    notes = %s
                WHERE application_id = %s
            """, (
                request.form.get("status") or "Applied",
                request.form.get("response_date") or None,
                request.form.get("interview_date") or None,
                request.form.get("notes") or None,
                application_id
            ))

            connection.commit()
            cursor.close()
            connection.close()
            flash("Application updated successfully!")
            return redirect(url_for("applications"))

    cursor.execute("""
        SELECT job_id, job_title
        FROM jobs
        ORDER BY job_title
    """)
    jobs_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            a.application_id,
            a.job_id,
            a.application_date,
            a.status,
            a.resume_version,
            a.cover_letter_sent,
            a.response_date,
            a.interview_date,
            a.notes,
            j.job_title,
            c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_id DESC
    """)
    applications_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "applications.html",
        applications=applications_list,
        jobs=jobs_list
    )
@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    connection = get_db_connection()

    if connection is None:
        return "Database connection failed.", 500

    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            cursor.execute("""
                INSERT INTO contacts (
                    company_id, first_name, last_name, email,
                    phone, job_title, linkedin_url, notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form["company_id"],
                request.form["first_name"].strip(),
                request.form["last_name"].strip(),
                request.form.get("email") or None,
                request.form.get("phone") or None,
                request.form.get("job_title") or None,
                request.form.get("linkedin_url") or None,
                request.form.get("notes") or None
            ))

            connection.commit()
            cursor.close()
            connection.close()
            flash("Contact added successfully!")
            return redirect(url_for("contacts"))

        elif action == "update":
            contact_id = request.form.get("contact_id", type=int)

            cursor.execute("""
                UPDATE contacts
                SET company_id = %s,
                    first_name = %s,
                    last_name = %s,
                    email = %s,
                    phone = %s,
                    job_title = %s,
                    linkedin_url = %s,
                    notes = %s
                WHERE contact_id = %s
            """, (
                request.form["company_id"],
                request.form["first_name"].strip(),
                request.form["last_name"].strip(),
                request.form.get("email") or None,
                request.form.get("phone") or None,
                request.form.get("job_title") or None,
                request.form.get("linkedin_url") or None,
                request.form.get("notes") or None,
                contact_id
            ))

            connection.commit()
            cursor.close()
            connection.close()
            flash("Contact updated successfully!")
            return redirect(url_for("contacts"))

        elif action == "delete":
            contact_id = request.form.get("contact_id", type=int)

            cursor.execute(
                "DELETE FROM contacts WHERE contact_id = %s",
                (contact_id,)
            )

            connection.commit()
            cursor.close()
            connection.close()
            flash("Contact deleted successfully!")
            return redirect(url_for("contacts"))

    edit_id = request.args.get("edit", type=int)
    edit_contact = None

    if edit_id is not None:
        cursor.execute(
            "SELECT * FROM contacts WHERE contact_id = %s",
            (edit_id,)
        )
        edit_contact = cursor.fetchone()

    cursor.execute("""
        SELECT company_id, company_name
        FROM companies
        ORDER BY company_name
    """)
    companies_list = cursor.fetchall()

    cursor.execute("""
        SELECT c.*, co.company_name
        FROM contacts c
        JOIN companies co ON c.company_id = co.company_id
        ORDER BY c.contact_id DESC
    """)
    contacts_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "contacts.html",
        contacts=contacts_list,
        companies=companies_list,
        edit_contact=edit_contact
    )
@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    import json

    matched_jobs = []
    user_skills = []

    if request.method == "POST":
        skills_text = request.form.get("skills", "")
        user_skills = [
            skill.strip().lower()
            for skill in skills_text.split(",")
            if skill.strip()
        ]

        connection = get_db_connection()

        if connection is None:
            return "Database connection failed.", 500

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                j.job_id,
                j.job_title,
                j.job_type,
                j.requirements,
                c.company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            WHERE j.is_active = 1
            ORDER BY j.job_title
        """)

        jobs_list = cursor.fetchall()
        cursor.close()
        connection.close()

        for job in jobs_list:
            requirements = job["requirements"]
            required_skills = []

            if requirements:
                try:
                    if isinstance(requirements, str):
                        requirements = json.loads(requirements)

                    required_skills = requirements.get("skills", [])
                except (json.JSONDecodeError, AttributeError, TypeError):
                    required_skills = []

            required_skills = [
                skill.strip()
                for skill in required_skills
                if isinstance(skill, str) and skill.strip()
            ]

            normalized_required = {
                skill.lower() for skill in required_skills
            }

            matching_skills = [
                skill for skill in required_skills
                if skill.lower() in user_skills
            ]

            if normalized_required:
                match_percentage = round(
                    len(normalized_required.intersection(user_skills))
                    / len(normalized_required) * 100
                )
            else:
                match_percentage = 0

            job["required_skills"] = required_skills
            job["matching_skills"] = matching_skills
            job["match_percentage"] = match_percentage
            matched_jobs.append(job)

        matched_jobs.sort(
            key=lambda job: job["match_percentage"],
            reverse=True
        )

    return render_template(
        "job_match.html",
        matched_jobs=matched_jobs,
        user_skills=user_skills
    )
if __name__ == "__main__":
    app.run(debug=True, port=5001)

