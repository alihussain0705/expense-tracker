# Spec: Login and Logout

## Overview

Step 3 implements user login with session management and logout functionality. Students will add POST handling to the `/login` route to authenticate users against the database using email and password verification, establish Flask sessions upon successful authentication, and implement the `/logout` route to clear sessions and redirect users. This step completes the core authentication flow, enabling students to gate features behind login checks in subsequent steps.

## Depends on

- **Step 1 (Database Setup):** Requires `database/db.py` with `get_db()` and the `users` table schema with `password_hash` column.
- **Step 2 (Registration):** Requires working registration so test users can be created with hashed passwords.

## Routes

- `GET /login` — Display login form (already exists, modify to show form)
- `POST /login` — Handle form submission, verify email and password, create session on success, redirect to profile or dashboard — **public**
- `POST /logout` — Clear session, redirect to landing page — **logged-in only**

## Database changes

No new tables or schema changes. The `users` table created in Step 1 is used:
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

- **Modify:** `templates/login.html` — Add `name` attributes to form inputs (`email`, `password`), add error message display block, add submit button, basic styling
- **Modify:** `templates/base.html` — Add logout button to navbar for logged-in users, show login/register links for anonymous users, hide logout for anonymous users

## Files to change

- `app.py` — Implement POST handler for `/login` route with email/password verification and session creation; implement `/logout` route to clear session
- `templates/login.html` — Add form input names, add error message display block, add submit button
- `templates/base.html` — Add conditional navbar logic: show "Logout" button if user is in session, show "Login/Register" links if not
- `static/js/main.js` — Optional: add client-side validation for login form (email format hint)

## Files to create

- `tests/test_auth.py` — Add login/logout tests (successful login, invalid email, wrong password, missing fields, logout clears session)

## New dependencies

- `werkzeug.security.check_password_hash` — Already included in Flask; used for password verification

No new pip packages required.

## Rules for implementation

- No SQLAlchemy or ORMs; use parameterized SQLite queries only
- Passwords must be verified with `werkzeug.security.check_password_hash()`
- Server-side validation is mandatory (email exists, password correct)
- Use `flask.session` to store user ID after successful login: `session['user_id'] = user_id`
- Session must be encrypted using `SECRET_KEY` (already set in `app.py`)
- On successful login, redirect to a dashboard/profile route (students will build this in Step 4)
- On error (email not found, password mismatch), re-render the login form with error messages
- Logout route must clear the session: `session.clear()` or `session.pop('user_id', None)`
- Logout must redirect to landing page (`/`)
- Use CSS variables — never hardcode hex values
- All templates must extend `base.html`
- Use `request.method == 'POST'` to distinguish form submission from page load
- Use `session.get('user_id')` to check if user is logged in (returns None if not)
- Navbar should conditionally render logout button vs login/register links based on session state

## Definition of done

- [ ] GET `/login` route displays login form
- [ ] POST `/login` route handles form submission
- [ ] Form inputs have `name` attributes: `email`, `password`
- [ ] Server validates: email not empty, password not empty
- [ ] Server queries database for user by email
- [ ] Server uses `check_password_hash()` to verify password against stored hash
- [ ] On successful authentication, user ID is stored in `session['user_id']`
- [ ] On success, user is redirected to `/profile` (or dashboard route)
- [ ] On error, login form is re-rendered with error message (e.g., "Invalid email or password")
- [ ] Logout route (`POST /logout`) clears session and redirects to landing page
- [ ] Navbar shows "Logout" button only when user is logged in (session has user_id)
- [ ] Navbar shows "Login/Register" links only when user is not logged in
- [ ] Test file `tests/test_auth.py` has at least 5 passing tests covering login/logout cases
- [ ] Test cases include: successful login, login with wrong password, login with non-existent email, logout clears session, missing form fields
- [ ] All tests pass: `pytest tests/test_auth.py -v`
- [ ] App runs without errors: `python app.py`
- [ ] Manual test: log in with demo user (demo@spendly.com / demo123) and confirm session is set
- [ ] Manual test: click logout and confirm redirect to landing page and session cleared
- [ ] Manual test: attempt login with wrong password and see error message
- [ ] Manual test: attempt login with non-existent email and see error message
