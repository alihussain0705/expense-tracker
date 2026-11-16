from flask import Flask, render_template, request, redirect, url_for, session
from database.db import get_db, init_db, seed_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spendly-dev-secret-key-change-in-production'

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Helper Functions                                                    #
# ------------------------------------------------------------------ #

def format_inr(amount):
    """Format amount as Indian Rupees with comma separators."""
    return f"₹{amount:,.2f}"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration via GET (form display) and POST (form submission)."""
    # Redirect logged-in users away from registration page
    if session.get('user_id'):
        return redirect(url_for("landing"))

    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        error = None

        # Validation
        if not name:
            error = "Name is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif not password_confirm:
            error = "Password confirmation is required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != password_confirm:
            error = "Passwords do not match."
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            error = "Invalid email format."

        # Check if email already exists
        if not error:
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    error = "Email is already registered."
                db.close()
            except sqlite3.Error as e:
                error = "Database error. Please try again."

        # Insert user if no errors
        if not error:
            try:
                password_hash = generate_password_hash(password)
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, password_hash)
                )
                db.commit()
                db.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Email is already registered."
            except sqlite3.Error as e:
                error = "Database error. Please try again."

        # Re-render form with error message
        return render_template("register.html", error=error)

    # GET request: display the form
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login via GET (form display) and POST (form submission)."""
    # Redirect logged-in users away from login page
    if session.get('user_id'):
        return redirect(url_for("landing"))

    if request.method == "POST":
        # Extract form data
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        error = None

        # Validation
        if not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."

        # Query database and verify password
        if not error:
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
                db.close()

                if user is None:
                    error = "Invalid email or password."
                elif not check_password_hash(user[1], password):
                    error = "Invalid email or password."
            except sqlite3.Error as e:
                error = "Database error. Please try again."

        # Create session on success
        if not error:
            session['user_id'] = user[0]
            return redirect(url_for("landing"))

        # Re-render form with error message
        return render_template("login.html", error=error)

    # GET request: display the form
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

@app.route("/logout", methods=["POST"])
def logout():
    """Clear user session and redirect to landing page."""
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Display and handle user profile updates with expense overview."""
    # Auth gate: redirect unauthenticated users to login
    if not session.get('user_id'):
        return redirect(url_for("login"))

    user_id = session['user_id']

    if request.method == "POST":
        # Extract and clean form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        error = None

        # Validation
        if not name:
            error = "Name is required."
        elif len(name) > 100:
            error = "Name must be 100 characters or less."
        elif not email:
            error = "Email is required."
        elif not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            error = "Invalid email format."

        # Check email uniqueness (excluding current user)
        if not error:
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "SELECT id FROM users WHERE email = ? AND id != ?",
                    (email, user_id)
                )
                if cursor.fetchone():
                    error = "Email is already in use."
                db.close()
            except sqlite3.Error as e:
                error = "Database error. Please try again."

        # Update database if no errors
        if not error:
            try:
                db = get_db()
                cursor = db.cursor()
                cursor.execute(
                    "UPDATE users SET name = ?, email = ? WHERE id = ?",
                    (name, email, user_id)
                )
                db.commit()
                db.close()
                # After successful update, redirect to profile to show updated data
                return redirect(url_for("profile"))
            except sqlite3.IntegrityError:
                error = "Email is already in use."
            except sqlite3.Error as e:
                error = "Database error. Please try again."

        # Re-render form with error
        return render_template("profile.html", error=error, name=name, email=email)

    # GET request: fetch user data and display profile with expense overview
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch user profile
        cursor.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            # User deleted while session active (edge case)
            session.clear()
            db.close()
            return redirect(url_for("login"))

        # Fetch expense totals
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,)
        )
        expense_totals = cursor.fetchone()

        # Fetch category breakdown (sorted by amount DESC)
        cursor.execute(
            "SELECT category, COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,)
        )
        category_breakdown = cursor.fetchall()

        # Fetch recent transactions (last 5, sorted by date DESC)
        cursor.execute(
            "SELECT id, date, category, description, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT 5",
            (user_id,)
        )
        recent_transactions = cursor.fetchall()

        db.close()

        # Parse created_at (format: YYYY-MM-DD HH:MM:SS) into readable date
        created_date = user['created_at'].split(' ')[0]  # Extract YYYY-MM-DD
        parsed_date = datetime.strptime(created_date, "%Y-%m-%d")
        formatted_date = parsed_date.strftime("%B %d, %Y")

        # Format amounts for display
        total_spent_formatted = format_inr(expense_totals['total'])

        # Format category breakdown amounts (convert Row objects to dicts for modification)
        formatted_categories = []
        for category in category_breakdown:
            cat_dict = dict(category)
            cat_dict['total_formatted'] = format_inr(cat_dict['total'])
            formatted_categories.append(cat_dict)
        category_breakdown = formatted_categories

        # Format recent transaction amounts and dates
        formatted_transactions = []
        for transaction in recent_transactions:
            trans_dict = dict(transaction)
            trans_dict['amount_formatted'] = format_inr(trans_dict['amount'])
            trans_date = datetime.strptime(trans_dict['date'], "%Y-%m-%d")
            trans_dict['date_formatted'] = trans_date.strftime("%b %d, %Y")
            formatted_transactions.append(trans_dict)
        recent_transactions = formatted_transactions

        return render_template(
            "profile.html",
            user=user,
            formatted_date=formatted_date,
            expense_totals=expense_totals,
            category_breakdown=category_breakdown,
            recent_transactions=recent_transactions,
            total_spent_formatted=total_spent_formatted
        )

    except sqlite3.Error as e:
        session.clear()
        return redirect(url_for("login"))


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
