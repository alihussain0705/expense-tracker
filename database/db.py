import sqlite3
import os
from werkzeug.security import generate_password_hash


def get_db():
    """
    Opens a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A database connection with row_factory set and foreign keys enabled.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", "spendly.db")
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    """
    Initializes the database by creating tables if they don't exist.
    Safe to call multiple times.
    """
    db = get_db()
    cursor = db.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Create expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    db.commit()
    db.close()


def seed_db():
    """
    Seeds the database with sample data if it hasn't been seeded yet.
    Prevents duplicate inserts on repeated calls.
    """
    db = get_db()
    cursor = db.cursor()

    # Check if users table already has data
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    if user_count > 0:
        db.close()
        return  # Already seeded, prevent duplicates

    # Insert demo user
    demo_password_hash = generate_password_hash("demo123")
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", demo_password_hash)
    )
    db.commit()

    # Get the demo user's ID
    cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",))
    user_id = cursor.fetchone()[0]

    # Insert 8 sample expenses covering all categories
    sample_expenses = [
        (user_id, 450.00, "Food", "2026-11-01", "Groceries from local market"),
        (user_id, 280.00, "Transport", "2026-11-02", "Uber ride to office"),
        (user_id, 1500.00, "Bills", "2026-11-03", "Electricity bill"),
        (user_id, 200.00, "Health", "2026-11-04", "Gym membership"),
        (user_id, 600.00, "Entertainment", "2026-11-05", "Movie tickets and popcorn"),
        (user_id, 1200.00, "Shopping", "2026-11-08", "Winter clothes"),
        (user_id, 350.00, "Food", "2026-11-10", "Restaurant dinner"),
        (user_id, 100.00, "Other", "2026-11-14", "Book purchase"),
    ]

    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        sample_expenses
    )
    db.commit()
    db.close()
