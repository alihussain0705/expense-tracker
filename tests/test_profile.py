import pytest
from database.db import get_db
from werkzeug.security import generate_password_hash
import sqlite3


class TestProfile:
    """Tests for user profile page (Step 4 Enhanced)."""

    def test_profile_redirect_if_not_logged_in(self, client):
        """GET /profile should redirect unauthenticated users to /login."""
        response = client.get("/profile")
        assert response.status_code == 302
        assert response.location.endswith("/login")

    def test_profile_get_logged_in(self, app, client):
        """GET /profile should display profile page for logged-in user."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # Demo user ID from seed_db()

        response = client.get("/profile")
        assert response.status_code == 200
        assert b"My Profile" in response.data
        assert b"Manage your account information" in response.data
        assert b"Demo User" in response.data  # Seeded demo user
        assert b"demo@spendly.com" in response.data
        assert b"Member Since" in response.data

    def test_profile_displays_formatted_date(self, app, client):
        """GET /profile should format created_at as readable date."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get("/profile")
        assert response.status_code == 200
        # Should contain a month name and year (date format: "Month DD, YYYY")
        assert any(month in response.data.decode() for month in [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])

    def test_profile_edit_form_present(self, client):
        """GET /profile should include edit form with name and email fields."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get("/profile")
        assert response.status_code == 200
        assert b'<form method="POST"' in response.data
        assert b'name="name"' in response.data
        assert b'name="email"' in response.data
        assert b'type="submit"' in response.data

    def test_profile_update_valid_name(self, app, client):
        """POST /profile should update name and redirect."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.post("/profile", data={
            "name": "Updated Name",
            "email": "demo@spendly.com"  # Keep email same
        })
        assert response.status_code == 302
        assert response.location.endswith("/profile")

        # Verify database update
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT name FROM users WHERE id = ?", (1,))
            user = cursor.fetchone()
            db.close()
            assert user['name'] == "Updated Name"

    def test_profile_update_valid_email(self, app, client):
        """POST /profile should update email and redirect."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.post("/profile", data={
            "name": "Demo User",  # Keep name same
            "email": "newemail@spendly.com"
        })
        assert response.status_code == 302
        assert response.location.endswith("/profile")

        # Verify database update
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT email FROM users WHERE id = ?", (1,))
            user = cursor.fetchone()
            db.close()
            assert user['email'] == "newemail@spendly.com"

    def test_profile_update_both_name_and_email(self, app, client):
        """POST /profile should update both name and email."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.post("/profile", data={
            "name": "New Name",
            "email": "newboth@spendly.com"
        })
        assert response.status_code == 302

        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT name, email FROM users WHERE id = ?", (1,))
            user = cursor.fetchone()
            db.close()
            assert user['name'] == "New Name"
            assert user['email'] == "newboth@spendly.com"

    def test_profile_update_no_change(self, app, client):
        """POST /profile should allow no-op update (same values)."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        # Submit same name and email as current
        response = client.post("/profile", data={
            "name": "Demo User",
            "email": "demo@spendly.com"
        })
        assert response.status_code == 302  # Still redirects successfully

    def test_profile_update_invalid_missing_name(self, client):
        """POST /profile with missing name should show error."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.post("/profile", data={
            "name": "",
            "email": "demo@spendly.com"
        })
        assert response.status_code == 200
        assert b"Name is required" in response.data

    def test_profile_update_invalid_missing_email(self, client):
        """POST /profile with missing email should show error."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.post("/profile", data={
            "name": "Demo User",
            "email": ""
        })
        assert response.status_code == 200
        assert b"Email is required" in response.data

    def test_profile_update_invalid_email_format(self, client):
        """POST /profile with invalid email format should show error."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.post("/profile", data={
            "name": "Demo User",
            "email": "invalid-email"
        })
        assert response.status_code == 200
        assert b"Invalid email format" in response.data

    def test_profile_update_duplicate_email(self, app, client):
        """POST /profile with email from another user should show error."""
        # First, create a second user in the database
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("Second User", "second@spendly.com", generate_password_hash("test123"))
            )
            db.commit()
            db.close()

        # Try to update demo user's email to second user's email
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.post("/profile", data={
            "name": "Demo User",
            "email": "second@spendly.com"
        })
        assert response.status_code == 200
        assert b"Email is already in use" in response.data

        # Verify no update occurred
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT email FROM users WHERE id = ?", (1,))
            user = cursor.fetchone()
            db.close()
            assert user['email'] == "demo@spendly.com"  # Unchanged

    def test_profile_post_redirect_if_not_logged_in(self, client):
        """POST /profile should redirect unauthenticated users to /login."""
        response = client.post("/profile", data={
            "name": "Test",
            "email": "test@example.com"
        }, follow_redirects=False)
        assert response.status_code == 302
        assert response.location.endswith("/login")

    # ===== NEW TESTS FOR EXPENSE OVERVIEW =====

    def test_profile_displays_expense_overview(self, app, client):
        """GET /profile should display expense overview section when user has expenses."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # Demo user with 8 seeded expenses

        response = client.get("/profile")
        assert response.status_code == 200
        assert b"Your Expenses" in response.data
        assert b"Total Spent" in response.data
        assert b"Transactions" in response.data
        assert b"By Category" in response.data
        assert b"Recent Transactions" in response.data

    def test_profile_displays_total_spent_formatted(self, app, client):
        """GET /profile should display total spent in INR format (₹X,XXX.XX)."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get("/profile")
        assert response.status_code == 200
        # Demo user has 8 expenses totaling 4,680 INR (450+280+1500+200+600+1200+350+100)
        # Check for the rupee symbol using unicode escape
        assert "₹4,680.00".encode() in response.data

    def test_profile_displays_transaction_count(self, app, client):
        """GET /profile should display count of transactions."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get("/profile")
        assert response.status_code == 200
        # Demo user has 8 seeded expenses
        assert b"8" in response.data
        assert b"Transactions" in response.data

    def test_profile_displays_category_breakdown(self, app, client):
        """GET /profile should display category breakdown with amounts and counts."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get("/profile")
        assert response.status_code == 200
        # Should show all categories with totals (formatted as ₹)
        assert b"Food" in response.data
        assert b"Transport" in response.data
        assert b"Bills" in response.data
        assert b"Health" in response.data
        assert b"Entertainment" in response.data
        assert b"Shopping" in response.data
        assert b"Other" in response.data
        # Verify amounts are formatted with rupee symbol
        assert "₹".encode() in response.data

    def test_profile_displays_recent_transactions(self, app, client):
        """GET /profile should display recent 5 transactions sorted by date DESC."""
        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get("/profile")
        assert response.status_code == 200
        assert b"Recent Transactions" in response.data
        # Should contain dates, categories, descriptions
        assert b"2026" in response.data  # Year from date
        # Verify transactions are present (description from seeded data)
        assert b"Groceries" in response.data or b"Restaurant" in response.data

    def test_profile_empty_state_no_expenses(self, app, client):
        """GET /profile should show empty state when user has no expenses."""
        # Create a new user with no expenses
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                ("New User", "newuser@test.com", generate_password_hash("test123"))
            )
            db.commit()
            new_user_id = cursor.lastrowid
            db.close()

        # Login as new user
        with client.session_transaction() as sess:
            sess['user_id'] = new_user_id

        response = client.get("/profile")
        assert response.status_code == 200
        # Should NOT display expense overview section
        assert b"Your Expenses" not in response.data
        assert b"Total Spent" not in response.data
        # But should show empty state message
        assert b"No expenses recorded yet" in response.data or b"Start tracking" in response.data
