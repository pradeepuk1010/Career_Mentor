"""SQLite persistence for the Career Mentor prototype.

On Streamlit Community Cloud, local files may not persist through app rebuilds or
restarts. Use a managed database for durable production storage.
"""
import json
import os
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).parent / "career_mentor.db"

def db_path():
    return Path(os.getenv("CAREER_MENTOR_DB", str(DEFAULT_DB)))

def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            data TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, category TEXT NOT NULL, due_date TEXT,
            notes TEXT, status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_of TEXT NOT NULL, wins TEXT, blockers TEXT, next_step TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        row = conn.execute("SELECT id FROM profile WHERE id=1").fetchone()
        if row is None:
            conn.execute("INSERT INTO profile (id, data) VALUES (1, ?)", (json.dumps(default_profile()),))

def default_profile():
    return {
        "name": "Student", "target_role": "Software Engineer", "stage": "4th year",
        "weekly_hours": 6, "career_goal": "Build job-ready skills and a portfolio project.",
        "interests": "AI, software development", "skills": ["Python", "Problem Solving"],
    }

def load_profile():
    init_db_if_needed()
    with connect() as conn:
        row = conn.execute("SELECT data FROM profile WHERE id=1").fetchone()
    try:
        data = json.loads(row["data"]) if row else default_profile()
    except (TypeError, json.JSONDecodeError):
        data = default_profile()
    base = default_profile()
    base.update(data)
    if not isinstance(base.get("skills"), list):
        base["skills"] = []
    return base

def init_db_if_needed():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1), data TEXT NOT NULL
        )""")
        row = conn.execute("SELECT id FROM profile WHERE id=1").fetchone()
        if row is None:
            conn.execute("INSERT INTO profile (id, data) VALUES (1, ?)", (json.dumps(default_profile()),))

def save_profile(data):
    payload = default_profile()
    payload.update(data)
    payload["skills"] = sorted(set(payload.get("skills", [])))
    with connect() as conn:
        conn.execute("""INSERT INTO profile (id, data) VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET data=excluded.data""", (json.dumps(payload),))

def list_goals():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM goals ORDER BY CASE status WHEN 'Open' THEN 0 ELSE 1 END, due_date, id DESC").fetchall()
    return [dict(r) for r in rows]

def add_goal(title, category, due_date, notes=""):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO goals (title, category, due_date, notes, status) VALUES (?, ?, ?, ?, 'Open')",
            (title, category, due_date, notes)
        )
        return cur.lastrowid

def update_goal_status(goal_id, status):
    if status not in {"Open", "Completed"}:
        raise ValueError("status must be Open or Completed")
    with connect() as conn:
        conn.execute("UPDATE goals SET status=? WHERE id=?", (status, int(goal_id)))

def delete_goal(goal_id):
    with connect() as conn:
        conn.execute("DELETE FROM goals WHERE id=?", (int(goal_id),))

def list_reflections():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM reflections ORDER BY week_of DESC, id DESC")
    return [dict(r) for r in rows.fetchall()]

def add_reflection(week_of, wins, blockers, next_step):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO reflections (week_of, wins, blockers, next_step) VALUES (?, ?, ?, ?)",
            (week_of, wins, blockers, next_step)
        )
        return cur.lastrowid
