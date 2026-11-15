import sqlite3
import random
import os
from datetime import datetime
from werkzeug.security import generate_password_hash
from database.db import get_db

# Common Indian names across regions
FIRST_NAMES = [
    "Rahul", "Arjun", "Vikram", "Priya", "Anjali", "Sanjay",
    "Isha", "Rohan", "Neha", "Aditya", "Divya", "Manish",
    "Shruti", "Karan", "Pooja", "Akshay", "Sneha", "Abhishek",
    "Riya", "Nikhil", "Deepika", "Varun", "Sakshi", "Aryan",
    "Amrita", "Harsh", "Nisha", "Alok", "Tanvi", "Rajesh"
]

LAST_NAMES = [
    "Sharma", "Singh", "Patel", "Kumar", "Gupta", "Reddy",
    "Verma", "Rao", "Desai", "Nair", "Iyer", "Pillai",
    "Kapoor", "Khan", "Joshi", "Pandey", "Mishra", "Bhat",
    "Yadav", "Trivedi", "Agarwal", "Chopra", "Saxena", "Mahajan"
]

def generate_unique_user():
    """Generate a random Indian user with unique email."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    email_suffix = random.randint(10, 999)

    name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{email_suffix}@gmail.com"
    password_hash = generate_password_hash("password123")

    return name, email, password_hash

def email_exists(db, email):
    """Check if email already exists in the database."""
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
    return cursor.fetchone()[0] > 0

def seed_random_user():
    """Generate and insert a unique random Indian user into the database."""
    db = get_db()

    # Generate user until we find a unique email
    attempts = 0
    max_attempts = 100

    while attempts < max_attempts:
        name, email, password_hash = generate_unique_user()

        if not email_exists(db, email):
            break

        attempts += 1
    else:
        db.close()
        print("❌ Failed to generate unique email after 100 attempts")
        return

    # Insert the user
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        db.commit()

        # Retrieve the inserted user's ID
        user_id = cursor.lastrowid

        print("✅ User created successfully!")
        print(f"   ID:    {user_id}")
        print(f"   Name:  {name}")
        print(f"   Email: {email}")

    except sqlite3.IntegrityError as e:
        db.rollback()
        print(f"❌ Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_random_user()
