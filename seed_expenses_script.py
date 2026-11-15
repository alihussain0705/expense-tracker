import sqlite3
import random
import sys
from datetime import datetime, timedelta
from database.db import get_db

# Parse arguments
user_id = 2
count = 5
months = 3

# Step 2: Verify user exists
db = get_db()
cursor = db.cursor()
cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
user = cursor.fetchone()

if not user:
    print(f"No user found with id {user_id}.")
    db.close()
    sys.exit(1)

# Step 3: Generate and insert expenses
categories = {
    "Food": {"range": (50, 800), "weight": 6, "descriptions": [
        "Groceries from market", "Restaurant dinner", "Street food",
        "Supermarket shopping", "Cafe lunch", "Home delivery meal"
    ]},
    "Transport": {"range": (20, 500), "weight": 4, "descriptions": [
        "Uber ride", "Auto rickshaw", "Bus pass", "Taxi fare",
        "Train ticket", "Bike maintenance"
    ]},
    "Bills": {"range": (200, 3000), "weight": 3, "descriptions": [
        "Electricity bill", "Internet bill", "Water bill",
        "Phone bill", "Gas bill", "Rent deposit"
    ]},
    "Health": {"range": (100, 2000), "weight": 2, "descriptions": [
        "Doctor visit", "Gym membership", "Medicine",
        "Lab test", "Dental checkup", "Hospital fees"
    ]},
    "Entertainment": {"range": (100, 1500), "weight": 2, "descriptions": [
        "Movie tickets", "Concert", "Gaming", "Streaming subscription",
        "Book purchase", "Sports event"
    ]},
    "Shopping": {"range": (200, 5000), "weight": 3, "descriptions": [
        "Winter clothes", "Electronics", "Home decor",
        "Shoes", "Accessories", "Furniture"
    ]},
    "Other": {"range": (50, 1000), "weight": 1, "descriptions": [
        "Miscellaneous", "Gift", "Tips", "Donation",
        "Repairs", "Stationery"
    ]}
}

# Create weighted category list
weighted_categories = []
for cat, data in categories.items():
    weighted_categories.extend([cat] * data["weight"])

# Generate expenses
expenses = []
today = datetime.now()
start_date = today - timedelta(days=30 * months)

for _ in range(count):
    # Random date within the past months
    random_days = random.randint(0, (today - start_date).days)
    expense_date = start_date + timedelta(days=random_days)
    date_str = expense_date.strftime("%Y-%m-%d")

    # Random category
    category = random.choice(weighted_categories)
    amount_range = categories[category]["range"]
    amount = random.uniform(amount_range[0], amount_range[1])

    # Random description
    description = random.choice(categories[category]["descriptions"])

    expenses.append((user_id, amount, category, date_str, description))

# Step 3: Insert all expenses in a transaction
try:
    cursor = db.cursor()
    cursor.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )
    db.commit()

    # Get the inserted records
    cursor.execute(
        "SELECT id, amount, category, date, description FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, min(5, count))
    )
    inserted_records = cursor.fetchall()

    # Step 4: Confirm
    print(f"✅ Successfully inserted {count} expenses for user {user_id}")

    # Date range
    dates = [exp[3] for exp in expenses]
    min_date = min(dates)
    max_date = max(dates)
    print(f"📅 Date range: {min_date} to {max_date}")

    print("\n📊 Sample of inserted records:")
    for rec in inserted_records:
        print(f"   ID: {rec[0]}, Amount: ₹{rec[1]:.2f}, Category: {rec[2]}, Date: {rec[3]}, Description: {rec[4]}")

except sqlite3.Error as e:
    db.rollback()
    print(f"❌ Database error: {e}")
    sys.exit(1)
finally:
    db.close()
