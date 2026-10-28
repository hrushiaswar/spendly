import sqlite3

import pytest

from database import db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    return db


def test_init_db_creates_tables(temp_db):
    temp_db.init_db()
    conn = temp_db.get_db()
    tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"users", "expenses"} <= tables


def test_init_db_is_idempotent(temp_db):
    temp_db.init_db()
    temp_db.init_db()  # should not raise


def test_seed_db_inserts_demo_data(temp_db):
    temp_db.init_db()
    temp_db.seed_db()
    conn = temp_db.get_db()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    expense_count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    conn.close()
    assert user_count == 1
    assert expense_count == 8


def test_seed_db_does_not_duplicate(temp_db):
    temp_db.init_db()
    temp_db.seed_db()
    temp_db.seed_db()
    conn = temp_db.get_db()
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    assert user_count == 1


def test_duplicate_email_raises_integrity_error(temp_db):
    temp_db.init_db()
    conn = temp_db.get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("A", "dup@example.com", "hash"),
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("B", "dup@example.com", "hash"),
        )
    conn.close()


def test_invalid_user_id_raises_foreign_key_error(temp_db):
    temp_db.init_db()
    conn = temp_db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (9999, 10.0, "Food", "2026-10-01"),
        )
    conn.close()
