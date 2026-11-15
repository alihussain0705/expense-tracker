import pytest
from app import app as flask_app


class TestRegistration:
    """Test suite for user registration functionality."""

    def test_register_get(self, client):
        """Test that GET /register displays the registration form."""
        response = client.get("/register")
        assert response.status_code == 200
        assert b"Create your account" in response.data
        assert b'name="name"' in response.data
        assert b'name="email"' in response.data
        assert b'name="password"' in response.data
        assert b'name="password_confirm"' in response.data

    def test_register_success(self, app, client):
        """Test successful user registration with valid data."""
        response = client.post(
            "/register",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123",
                "password_confirm": "password123",
            }
        )
        # Should redirect to login on success
        assert response.status_code == 302
        assert response.location.endswith("/login")

        # Verify user was created in database
        with app.app_context():
            from database.db import get_db
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT name, email FROM users WHERE email = ?", ("john@example.com",))
            user = cursor.fetchone()
            db.close()

            assert user is not None
            assert user[0] == "John Doe"
            assert user[1] == "john@example.com"

    def test_register_duplicate_email(self, app, client):
        """Test that registering with an existing email shows an error."""
        # First registration
        client.post(
            "/register",
            data={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        # Try to register with the same email
        response = client.post(
            "/register",
            data={
                "name": "Bob",
                "email": "alice@example.com",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        assert response.status_code == 200
        assert b"Email is already registered" in response.data

    def test_register_password_mismatch(self, client):
        """Test that mismatched passwords show an error."""
        response = client.post(
            "/register",
            data={
                "name": "Charlie",
                "email": "charlie@example.com",
                "password": "password123",
                "password_confirm": "different456",
            }
        )

        assert response.status_code == 200
        assert b"Passwords do not match" in response.data

    def test_register_missing_name(self, client):
        """Test that missing name shows an error."""
        response = client.post(
            "/register",
            data={
                "name": "",
                "email": "user@example.com",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        assert response.status_code == 200
        assert b"Name is required" in response.data

    def test_register_missing_email(self, client):
        """Test that missing email shows an error."""
        response = client.post(
            "/register",
            data={
                "name": "User",
                "email": "",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        assert response.status_code == 200
        assert b"Email is required" in response.data

    def test_register_missing_password(self, client):
        """Test that missing password shows an error."""
        response = client.post(
            "/register",
            data={
                "name": "User",
                "email": "user@example.com",
                "password": "",
                "password_confirm": "password123",
            }
        )

        assert response.status_code == 200
        assert b"Password is required" in response.data

    def test_register_missing_password_confirm(self, client):
        """Test that missing password confirmation shows an error."""
        response = client.post(
            "/register",
            data={
                "name": "User",
                "email": "user@example.com",
                "password": "password123",
                "password_confirm": "",
            }
        )

        assert response.status_code == 200
        assert b"Password confirmation is required" in response.data

    def test_register_short_password(self, client):
        """Test that passwords shorter than 6 characters show an error."""
        response = client.post(
            "/register",
            data={
                "name": "User",
                "email": "user@example.com",
                "password": "pass1",
                "password_confirm": "pass1",
            }
        )

        assert response.status_code == 200
        assert b"Password must be at least 6 characters" in response.data

    def test_register_invalid_email(self, client):
        """Test that invalid email formats show an error."""
        response = client.post(
            "/register",
            data={
                "name": "User",
                "email": "invalid-email",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        assert response.status_code == 200
        assert b"Invalid email format" in response.data

    def test_register_whitespace_trimmed(self, app, client):
        """Test that leading/trailing whitespace is trimmed from name and email."""
        response = client.post(
            "/register",
            data={
                "name": "  John Doe  ",
                "email": "  john@example.com  ",
                "password": "password123",
                "password_confirm": "password123",
            }
        )

        assert response.status_code == 302

        # Verify user was created with trimmed values
        with app.app_context():
            from database.db import get_db
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT name, email FROM users WHERE email = ?", ("john@example.com",))
            user = cursor.fetchone()
            db.close()

            assert user is not None
            assert user[0] == "John Doe"
            assert user[1] == "john@example.com"
