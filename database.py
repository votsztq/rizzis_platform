import sqlite3
import os
from datetime import datetime

DB_FILE = "rizzis_platform.db"


def get_connection():
    """Establishes a safe connection to the local SQLite file database."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def initialize_database():
    """Creates the structural tables for your tracking system if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Core Task Management Table with Rich Text Detail Fields
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tasks
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       due_date
                       TEXT
                       NOT
                       NULL,
                       priority
                       TEXT
                       NOT
                       NULL,
                       create_date
                       TEXT
                       NOT
                       NULL,
                       category
                       TEXT
                       NOT
                       NULL,
                       status
                       TEXT
                       DEFAULT
                       'Active',
                       notes
                       TEXT
                       DEFAULT
                       '',
                       description
                       TEXT
                       DEFAULT
                       '',
                       important_notes
                       TEXT
                       DEFAULT
                       '',
                       reference_link
                       TEXT
                       DEFAULT
                       ''
                   )
                   """)

    # 2. AUX Stopwatch Runtime Log Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS aux_logs
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       log_date
                       TEXT
                       NOT
                       NULL,
                       aux_unit
                       TEXT
                       NOT
                       NULL,
                       duration_seconds
                       INTEGER
                       DEFAULT
                       0
                   )
                   """)

    # 3. Educational Portal Fees Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS education_fees
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       fee_pending
                       TEXT
                       NOT
                       NULL,
                       amount
                       REAL
                       DEFAULT
                       0.0,
                       university
                       TEXT
                       NOT
                       NULL,
                       due_date
                       TEXT
                       NOT
                       NULL,
                       semester
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    # 4. Educational Portal Syllabus Notes Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS education_syllabus
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       semester
                       TEXT
                       NOT
                       NULL,
                       subject
                       TEXT
                       NOT
                       NULL,
                       details
                       TEXT
                       DEFAULT
                       ''
                   )
                   """)

    # 5. Career Portal Ledger Table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS career_notes
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       job_role
                       TEXT
                       NOT
                       NULL,
                       company_name
                       TEXT
                       NOT
                       NULL,
                       field
                       TEXT
                       NOT
                       NULL,
                       resume_submitted
                       TEXT
                       NOT
                       NULL,
                       follow_up_date
                       TEXT
                       NOT
                       NULL
                   )
                   """)

    conn.commit()
    conn.close()


# --- TASK ENGINE OPERATIONAL FUNCTIONS ---

def add_task(title, due_date, priority, category, description="", important_notes="", reference_link=""):
    conn = get_connection()
    cursor = conn.cursor()
    create_date = datetime.now().strftime("%d/%m/%Y")

    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN description TEXT DEFAULT ''")
        cursor.execute("ALTER TABLE tasks ADD COLUMN important_notes TEXT DEFAULT ''")
        cursor.execute("ALTER TABLE tasks ADD COLUMN reference_link TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
                   INSERT INTO tasks (title, due_date, priority, create_date, category, status, description,
                                      important_notes, reference_link)
                   VALUES (?, ?, ?, ?, ?, 'Active', ?, ?, ?)
                   """,
                   (title, due_date, priority, create_date, category, description, important_notes, reference_link))
    conn.commit()
    conn.close()


def get_active_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, title, due_date, priority, create_date, category, notes, description, important_notes, reference_link FROM tasks WHERE status = 'Active'")
    except sqlite3.OperationalError:
        cursor.execute(
            "SELECT id, title, due_date, priority, create_date, category, notes, '', '', '' FROM tasks WHERE status = 'Active'")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_task_details(task_id, due_date, notes, description, important_notes, reference_link):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   UPDATE tasks
                   SET due_date        = ?,
                       notes           = ?,
                       description     = ?,
                       important_notes = ?,
                       reference_link  = ?
                   WHERE id = ?
                   """, (due_date, notes, description, important_notes, reference_link, task_id))
    conn.commit()
    conn.close()


def complete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'Complete' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# --- ANALYTICS & AUX STOPWATCH OPERATIONAL FUNCTIONS ---

def get_completed_tasks_count(target_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Complete' AND due_date = ?", (target_date,))
    res = cursor.fetchone()
    conn.close()
    # FIX: Extract the raw number element out of the tuple container safely
    return res[0] if res else 0

def get_assigned_tasks_today_count(today_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE create_date = ? OR (status = 'Complete' AND due_date = ?)", (today_str, today_str))
    res = cursor.fetchone()
    conn.close()
    # FIX: Extract the raw number element out of the tuple container safely
    return res[0] if res else 0



def get_completed_tasks_by_category():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) FROM tasks WHERE status = 'Complete' GROUP BY category")
    data = dict(cursor.fetchall())
    conn.close()
    return data


def log_aux_time(date_str, unit_name, seconds_to_add):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, duration_seconds FROM aux_logs WHERE log_date = ? AND aux_unit = ?",
                   (date_str, unit_name))
    row = cursor.fetchone()
    if row:
        new_seconds = row[1] + seconds_to_add
        cursor.execute("UPDATE aux_logs SET duration_seconds = ? WHERE id = ?", (new_seconds, row[0]))
    else:
        cursor.execute("INSERT INTO aux_logs (log_date, aux_unit, duration_seconds) VALUES (?, ?, ?)",
                       (date_str, unit_name, seconds_to_add))
    conn.commit()
    conn.close()


def get_aux_time_matrix(date_str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT aux_unit, duration_seconds FROM aux_logs WHERE log_date = ?", (date_str,))
    data = dict(cursor.fetchall())
    conn.close()
    return data


# --- EDUCATIONAL PORTAL METHODS ---

def get_education_fees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fee_pending, amount, university, due_date, semester FROM education_fees")
    rows = cursor.fetchall()
    conn.close()
    return rows


def sync_education_fee_row(row_id, fee_pending, amount, university, due_date, semester):
    conn = get_connection()
    cursor = conn.cursor()
    if row_id is not None:
        cursor.execute("""
                       UPDATE education_fees
                       SET fee_pending = ?,
                           amount      = ?,
                           university  = ?,
                           due_date    = ?,
                           semester    = ?
                       WHERE id = ?
                       """, (fee_pending, amount, university, due_date, semester, row_id))
    else:
        cursor.execute("""
                       INSERT INTO education_fees (fee_pending, amount, university, due_date, semester)
                       VALUES (?, ?, ?, ?, ?)
                       """, (fee_pending, amount, university, due_date, semester))
    conn.commit()
    conn.close()


def delete_education_fee_row(row_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM education_fees WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()


def get_syllabus_notes(semester, subject_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT details, subject FROM education_syllabus WHERE semester = ? AND subject = ?",
                   (semester, subject_key))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    return "Click to add details", subject_key


def update_syllabus_notes(semester, subject_key, details, custom_title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM education_syllabus WHERE semester = ? AND subject = ?", (semester, subject_key))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE education_syllabus SET details = ?, subject = ? WHERE id = ?",
                       (details, custom_title, row[0]))
    else:
        cursor.execute("INSERT INTO education_syllabus (semester, subject, details) VALUES (?, ?, ?)",
                       (semester, custom_title, details))
    conn.commit()
    conn.close()


# --- CAREER PORTAL OPERATION METHODS ---

def get_career_notes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, job_role, company_name, field, resume_submitted, follow_up_date FROM career_notes")
    rows = cursor.fetchall()
    conn.close()
    return rows


def sync_career_note_row(row_id, job_role, company_name, field, resume_submitted, follow_up_date):
    conn = get_connection()
    cursor = conn.cursor()
    if row_id is not None:
        cursor.execute("""
                       UPDATE career_notes
                       SET job_role         = ?,
                           company_name     = ?,
                           field            = ?,
                           resume_submitted = ?,
                           follow_up_date   = ?
                       WHERE id = ?
                       """, (job_role, company_name, field, resume_submitted, follow_up_date, row_id))
    else:
        cursor.execute("""
                       INSERT INTO career_notes (job_role, company_name, field, resume_submitted, follow_up_date)
                       VALUES (?, ?, ?, ?, ?)
                       """, (job_role, company_name, field, resume_submitted, follow_up_date))
    conn.commit()
    conn.close()


def delete_career_note_row(row_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM career_notes WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()


# Run database configuration setup automatically upon startup
initialize_database()
