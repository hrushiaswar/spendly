import pytest

from database import db, queries


@pytest.fixture
def seeded_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    db.seed_db()
    return db


@pytest.fixture
def demo_user_id(seeded_db):
    conn = seeded_db.get_db()
    row = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)).fetchone()
    conn.close()
    return row["id"]


@pytest.fixture
def empty_user_id(seeded_db):
    conn = seeded_db.get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("No Expenses", "empty@spendly.com", "hash"),
    )
    conn.commit()
    row = conn.execute("SELECT id FROM users WHERE email = ?", ("empty@spendly.com",)).fetchone()
    conn.close()
    return row["id"]


# -- get_user_by_id ---------------------------------------------------------

def test_get_user_by_id_valid(demo_user_id):
    user = queries.get_user_by_id(demo_user_id)
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert user["member_since"]
    assert user["initials"] == "DU"


def test_get_user_by_id_missing(seeded_db):
    assert queries.get_user_by_id(9999) is None


# -- get_summary_stats -------------------------------------------------------

def test_get_summary_stats_with_expenses(demo_user_id):
    stats = queries.get_summary_stats(demo_user_id)
    assert stats["total_spent"] == pytest.approx(396.25)
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(empty_user_id):
    stats = queries.get_summary_stats(empty_user_id)
    assert stats == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


# -- get_recent_transactions --------------------------------------------------

def test_get_recent_transactions_with_expenses(demo_user_id):
    transactions = queries.get_recent_transactions(demo_user_id)
    assert len(transactions) == 8
    assert transactions[0]["description"] == "Dinner out"
    assert transactions[-1]["description"] == "Groceries"
    for tx in transactions:
        assert set(tx) == {"date", "description", "category", "amount"}
        assert tx["amount"].startswith("₹")


def test_get_recent_transactions_no_expenses(empty_user_id):
    assert queries.get_recent_transactions(empty_user_id) == []


# -- get_category_breakdown --------------------------------------------------

def test_get_category_breakdown_with_expenses(demo_user_id):
    breakdown = queries.get_category_breakdown(demo_user_id)
    names = [c["name"] for c in breakdown]
    assert set(names) == {"Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"}
    amounts = [float(c["amount"].replace("₹", "")) for c in breakdown]
    assert amounts == sorted(amounts, reverse=True)
    assert sum(c["pct"] for c in breakdown) == 100
    for c in breakdown:
        assert c["amount"].startswith("₹")


def test_get_category_breakdown_no_expenses(empty_user_id):
    assert queries.get_category_breakdown(empty_user_id) == []


# -- GET /profile route -------------------------------------------------------

def test_profile_redirects_when_not_logged_in(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_shows_real_demo_user_data(client):
    client.post("/login", data={"email": "demo@spendly.com", "password": "demo123"})
    response = client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
    assert "₹396.25" in body
    assert ">8<" in body or "8" in body
    assert "Bills" in body

    food_index = body.find("Dinner out")
    groceries_index = body.find("Groceries")
    assert food_index != -1 and groceries_index != -1
    assert food_index < groceries_index  # newest (Oct 25) appears before oldest (Oct 2)

    for category in ("Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"):
        assert category in body


def test_profile_shows_zero_state_for_new_user(client):
    client.post(
        "/register",
        data={"name": "New Person", "email": "newperson@example.com", "password": "password123"},
    )
    client.post("/login", data={"email": "newperson@example.com", "password": "password123"})
    response = client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "₹0.00" in body
    assert "New Person" in body
