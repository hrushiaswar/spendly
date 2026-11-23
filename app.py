from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)
app.secret_key = "dev-secret-key"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")

        if len(password) < 8:
            return render_template(
                "register.html", error="Password must be at least 8 characters."
            )

        if get_user_by_email(email) is not None:
            return render_template(
                "register.html", error="An account with this email already exists."
            )

        password_hash = generate_password_hash(password)
        conn = get_db()
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password.")

        session["user_id"] = user["id"]
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_info = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "member_since": "October 2026",
        "initials": "DU",
    }

    stats = [
        {"label": "Total spent", "value": "₹396.25"},
        {"label": "Transactions", "value": "8"},
        {"label": "Top category", "value": "Food"},
    ]

    transactions = [
        {"date": "Oct 25, 2026", "description": "Dinner out", "category": "Food", "amount": "₹32.75"},
        {"date": "Oct 22, 2026", "description": "Miscellaneous", "category": "Other", "amount": "₹15.00"},
        {"date": "Oct 20, 2026", "description": "New shoes", "category": "Shopping", "amount": "₹80.00"},
        {"date": "Oct 15, 2026", "description": "Movie tickets", "category": "Entertainment", "amount": "₹25.00"},
        {"date": "Oct 12, 2026", "description": "Pharmacy", "category": "Health", "amount": "₹60.00"},
        {"date": "Oct 7, 2026", "description": "Electricity bill", "category": "Bills", "amount": "₹120.00"},
        {"date": "Oct 5, 2026", "description": "Bus pass top-up", "category": "Transport", "amount": "₹18.00"},
        {"date": "Oct 2, 2026", "description": "Groceries", "category": "Food", "amount": "₹45.50"},
    ]

    categories = [
        {"name": "Bills", "amount": "₹120.00", "pct": 30},
        {"name": "Food", "amount": "₹78.25", "pct": 20},
        {"name": "Shopping", "amount": "₹80.00", "pct": 20},
        {"name": "Health", "amount": "₹60.00", "pct": 15},
        {"name": "Entertainment", "amount": "₹25.00", "pct": 6},
        {"name": "Transport", "amount": "₹18.00", "pct": 5},
        {"name": "Other", "amount": "₹15.00", "pct": 4},
    ]

    return render_template(
        "profile.html",
        user_info=user_info,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
