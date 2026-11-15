import pytest
import sqlite3
import os
import tempfile
from app import app as flask_app
from database.db import init_db


@pytest.fixture
def app():
    """Create and configure a test Flask app instance with temporary test database."""
    # Create a temporary database file for testing
    db_fd, db_path = tempfile.mkstemp()

    # Set environment variable to tell get_db() to use the test database
    original_db_path = os.environ.get('SPENDLY_DB_PATH')
    os.environ['SPENDLY_DB_PATH'] = db_path

    # Configure Flask app for testing
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key-for-testing-only'

    # Initialize the test database
    with flask_app.app_context():
        init_db()

    yield flask_app

    # Restore original environment
    if original_db_path is None:
        os.environ.pop('SPENDLY_DB_PATH', None)
    else:
        os.environ['SPENDLY_DB_PATH'] = original_db_path

    # Clean up: close the database and delete the temporary file
    try:
        os.close(db_fd)
    except:
        pass
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def client(app):
    """Create a test client for making requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()
