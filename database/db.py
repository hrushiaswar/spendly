import os
import sqlite3

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, os.pardir, "expense_tracker.db"))


def get_db():
    """Return a new SQLite connection with dict-like row access and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables if they don't already exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,
            date        TEXT NOT NULL,
            description TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    """Insert demo data for development. No-op if users already exist."""
    conn = get_db()
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cur.lastrowid

    sample_expenses = [
        (user_id, 45.50, "Food", "Groceries", "2026-10-02"),
        (user_id, 18.00, "Transport", "Bus pass top-up", "2026-10-05"),
        (user_id, 120.00, "Bills", "Electricity bill", "2026-10-07"),
        (user_id, 60.00, "Health", "Pharmacy", "2026-10-12"),
        (user_id, 25.00, "Entertainment", "Movie tickets", "2026-10-15"),
        (user_id, 80.00, "Shopping", "New shoes", "2026-10-20"),
        (user_id, 15.00, "Other", "Miscellaneous", "2026-10-22"),
        (user_id, 32.75, "Food", "Dinner out", "2026-10-25"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, description, date) "
        "VALUES (?, ?, ?, ?, ?)",
        sample_expenses,
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_db()
    print(f"Database initialized at {DB_PATH}")
