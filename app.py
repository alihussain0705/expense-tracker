from flask import Flask, render_template, request, redirect, url_for, session
from database.db import get_db, init_db, seed_db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spendly-dev-secret-key-change-in-production'

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration via GET (form display) and POST (form submission)."""
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


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


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
