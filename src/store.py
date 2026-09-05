import sqlite3
import json
from datetime import datetime

DB_PATH = "jobs.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            url TEXT,
            location TEXT,
            remote TEXT,
            tags TEXT,
            source TEXT,
            posted_date TEXT,
            first_seen TEXT
        )
    """
    )
    conn.commit()
    conn.close()

def get_known_ids() -> set:
    conn = get_connection()
    rows = conn.execute("SELECT id FROM jobs").fetchall()
    conn.close()
    return {row[0] for row in rows}


def save_job(job):
    conn = get_connection()
    conn.execute(
    """
    INSERT OR IGNORE INTO jobs (id, title, company, url, location, remote, tags, source, posted_date, first_seen)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            job.id,
            job.title,
            job.company,
            job.url,
            job.location,
            job.remote.name if job.remote else None,
            json.dumps(job.tags) if job.tags else None,
            job.source,
            job.posted_date.isoformat(),
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    