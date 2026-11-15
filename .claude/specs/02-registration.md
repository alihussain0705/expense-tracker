# Spec: Registration

## Overview

Step 2 implements user registration with server-side form handling, password hashing, and validation. Students will add POST handling to the `/register` route, validate form inputs (email format, password strength, password confirmation), hash passwords using werkzeug, and insert new users into the database. This step focuses on authentication mechanics and data persistence, setting up the foundation for login (Step 3) and session management.

## Depends on

- **Step 1 (Database Setup):** Requires `database/db.py` with `get_db()`, `init_db()`, and the `users` table schema.

## Routes

- `GET /register` — Display registration form (already exists, no changes)
- `POST /register` — Handle form submission, validate inputs, hash password, insert user into database, redirect to login on success — **public**

## Database changes

No new tables or schema changes. The `users` table created in Step 1 is used as-is:
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
)
```

## Templates

- **Modify:** `templates/register.html` — Add `name` attributes to form inputs, add client-side validation hints (email format check, password confirmation match), display error messages on failed registration.

## Files to change

- `app.py` — Add `SECRET_KEY` to Flask app, add POST handler to `/register` route with validation and database insert
- `templates/register.html` — Add form input names, add error message display block, add client-side validation
- `static/js/main.js` — Add client-side validation for registration form (email format, password match)

## Files to create

- `tests/test_auth.py` — Test file with registration tests (successful registration, duplicate email, missing fields, password mismatch, invalid email)

## New dependencies

- `werkzeug` — Already included in Flask; used for `generate_password_hash()`

No new pip packages required.

## Rules for implementation

- No SQLAlchemy or ORMs; use parameterized SQLite queries only
- Passwords must be hashed with `werkzeug.security.generate_password_hash()`
- Server-side validation is mandatory (email uniqueness, non-empty fields, password confirmation match)
- Client-side validation is a UX enhancement; server-side is the source of truth
- Use CSS variables — never hardcode hex values
- All templates must extend `base.html`
- Use `request.method == 'POST'` to distinguish form submission from page load
- Email validation: basic check (format like `user@domain.com`); full RFC validation not required
- Password requirements: minimum 6 characters (students can define their own policy)
- On success, redirect to `/login` with a success message or flash indicator
- On error (duplicate email, validation failure), re-render the form with error messages
- Do not commit plaintext passwords; always hash before database insert
- Use `INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)` with parameterized query to prevent SQL injection

## Definition of done

- [ ] POST `/register` route handles form submission
- [ ] Form inputs have `name` attributes: `name`, `email`, `password`, `password_confirm`
- [ ] Server validates: name not empty, email format valid, email not already in database, password at least 6 characters, password matches confirmation
- [ ] Passwords are hashed with `generate_password_hash()` before insertion
- [ ] On success, user is inserted into database and redirected to `/login`
- [ ] On error, form is re-rendered with error messages visible to user
- [ ] Client-side validation prevents form submission for obvious errors (email format, password mismatch)
- [ ] Duplicate email error is caught and displayed
- [ ] Test file `tests/test_auth.py` has at least 5 passing tests covering success and error cases
- [ ] All tests pass: `pytest tests/test_auth.py -v`
- [ ] App runs without errors: `python app.py` connects to database and server starts on port 5001
- [ ] Manual test: register a new user successfully and see redirect to login
- [ ] Manual test: attempt duplicate email and see error message
- [ ] Manual test: attempt mismatched passwords and see client-side validation or server-side error
