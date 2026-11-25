"""Pure query helpers for the profile page. No Flask imports here."""

from datetime import datetime

from database.db import get_db


def get_category_breakdown(user_id):
    """Return a list of {"name": str, "amount": "₹123.45", "pct": int}, one per category
    the user has spent in, ordered by amount descending. pct values must be integers
    that sum to exactly 100. Returns [] if the user has no expenses.
    """
    db = get_db()
    rows = db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses WHERE user_id = ? "
        "GROUP BY category ORDER BY total DESC",
        (user_id,),
    ).fetchall()
    db.close()

    if not rows:
        return []

    grand_total = sum(row["total"] for row in rows)

    breakdown = []
    rounded_pcts = []
    for row in rows:
        raw_pct = 100 * row["total"] / grand_total
        rounded_pcts.append(round(raw_pct))

    remainder = 100 - sum(rounded_pcts)
    rounded_pcts[0] += remainder

    for row, pct in zip(rows, rounded_pcts):
        breakdown.append(
            {
                "name": row["category"],
                "amount": f"₹{row['total']:.2f}",
                "pct": pct,
            }
        )

    return breakdown


def get_user_by_id(user_id):
    """Return {"name", "email", "member_since", "initials"} for the given user,
    or None if no such user exists.
    """
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    name = row["name"] or ""
    email = row["email"]
    created_at = row["created_at"]

    try:
        created_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        created_dt = datetime.strptime(created_at.split(" ")[0], "%Y-%m-%d")

    member_since = created_dt.strftime("%B %Y")

    words = name.split()
    initials = "".join(word[0].upper() for word in words[:2])

    return {
        "name": name,
        "email": email,
        "member_since": member_since,
        "initials": initials,
    }


def get_summary_stats(user_id):
    """Return {"total_spent": float, "transaction_count": int, "top_category": str}."""
    conn = get_db()
    try:
        totals_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total, COUNT(*) AS cnt "
            "FROM expenses WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        cnt = totals_row["cnt"]
        if cnt == 0:
            return {
                "total_spent": 0,
                "transaction_count": 0,
                "top_category": "—",
            }

        top_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? "
            "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    return {
        "total_spent": float(totals_row["total"]),
        "transaction_count": int(cnt),
        "top_category": top_row["category"],
    }


def get_recent_transactions(user_id, limit=10):
    """Return the user's most recent expenses, newest first.

    Each item: {"date": "Oct 25, 2026", "description": str, "category": str, "amount": "₹123.45"}.
    Returns [] if the user has no expenses.
    """
    db = get_db()
    rows = db.execute(
        "SELECT date, description, category, amount FROM expenses WHERE user_id = ? "
        "ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    db.close()

    if not rows:
        return []

    transactions = []
    for row in rows:
        dt = datetime.strptime(row["date"], "%Y-%m-%d")
        formatted_date = f"{dt:%b} {dt.day}, {dt:%Y}"
        transactions.append(
            {
                "date": formatted_date,
                "description": row["description"],
                "category": row["category"],
                "amount": f"₹{row['amount']:.2f}",
            }
        )

    return transactions
