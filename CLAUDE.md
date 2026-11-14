# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spendly** is an educational expense tracker web application built with Flask. It's a learning project structured in steps, with students progressively implementing database setup, authentication, and expense management features. The project uses SQLite for persistence and Jinja2 templates for server-side rendering.

The app is currently at the UI/routing stage — the landing, login, register, terms, and privacy pages are built. Placeholder routes exist for features students will implement in later steps (logout, profile, add/edit/delete expenses).

## Architecture

**Tech Stack:**
- Backend: Flask 3.1.3 (Python web framework)
- Frontend: Vanilla HTML/CSS/JavaScript (no build tools)
- Database: SQLite (to be implemented in Step 1)
- Testing: pytest + pytest-flask
- Styling: Custom CSS with design tokens (DM Sans + DM Serif Display fonts)

**Directory Structure:**
```
├── app.py                 # Main Flask app with all routes
├── database/
│   ├── __init__.py       # Empty; students add imports here
│   └── db.py             # Placeholder for DB functions (get_db, init_db, seed_db)
├── templates/
│   ├── base.html         # Base layout with nav, footer, blocks
│   ├── landing.html      # Home page with hero and YouTube modal
│   ├── login.html        # Login form
│   ├── register.html     # Registration form
│   ├── privacy.html      # Privacy Policy (legal page)
│   └── terms.html        # Terms and Conditions (legal page)
├── static/
│   ├── css/style.css     # All CSS (mobile-first, design tokens at root)
│   └── js/main.js        # Minimal; students add JS here
├── requirements.txt      # Python dependencies
└── .gitignore           # Excludes .DS_Store, __pycache__, *.pyc, etc.
```

**Key Design Patterns:**
- **Jinja2 template inheritance:** All pages extend `base.html`, which provides navbar, footer, and semantic blocks (title, head, content, scripts).
- **Design tokens:** CSS variables at `:root` define colors, fonts, spacing, and breakpoints. Consistent spacing use of 1rem base (16px).
- **Page structure:** Each route renders a template; no JSON API endpoints yet.
- **Styling approach:** Single `style.css` file organized in sections (Variables, Reset, Navbar, Footer, Forms, etc.). Mobile-first responsive design with media queries.

**Database Placeholder:**
`database/db.py` is empty and must be written by students. It should provide:
- `get_db()` — returns a SQLite connection with `row_factory=sqlite3.Row` and `PRAGMA foreign_keys=ON`
- `init_db()` — creates tables (users, expenses, categories) with `IF NOT EXISTS`
- `seed_db()` — inserts sample data for development

**Frontend (Current State):**
- Landing page includes a YouTube video modal ("See How It Works" button opens an embedded iframe).
- Login/register forms are unstyled placeholders (students will add client-side validation in later steps).
- Privacy and Terms pages are full legal content (already written).
- `main.js` is a placeholder; JavaScript will be added as features expand.

## Common Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask dev server (auto-reloads on file changes)
python app.py

# Runs on http://127.0.0.1:5001 with debug=True
```

### Testing
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v

# Run a specific test
pytest tests/test_auth.py::test_login_success -v

# Run with coverage (if coverage installed)
pytest --cov=. --cov-report=html
```

### Database (when implemented)
```bash
# In Python shell, after db.py is written:
from database.db import get_db, init_db, seed_db
import app

with app.app.app_context():
    init_db()    # Create tables
    seed_db()    # Insert sample data
    db = get_db()  # Use connection
```

## Important Notes for Development

### Routing and Views
- All routes are in `app.py` at the top level (no blueprints yet).
- Routes render Jinja2 templates; no JSON responses until later steps.
- Placeholder routes (logout, profile, add_expense, edit_expense, delete_expense) return plain strings — replace these with `render_template()` calls as features are implemented.

### Database Integration (Step 1)
When students write `database/db.py`:
- Must use SQLite3 with row_factory for dict-like access.
- Enable foreign keys: `PRAGMA foreign_keys=ON`.
- Use context manager pattern: `with get_db() as db: cursor = db.cursor()`.
- Tables needed: `users`, `expenses`, `categories`.
- Test with `pytest-flask` using fixtures that call `init_db()` in test app context.

### Authentication (Steps 2–3)
- No session management or password hashing yet.
- When implementing: use `flask.session` and `werkzeug.security.check_password_hash`.
- Login/register routes will need `request.method == 'POST'` handling and form validation.
- Set `SECRET_KEY` on the Flask app for session encryption.

### Styling Guidelines
- Design tokens in CSS `:root` — never use hardcoded hex colors in selectors.
- Mobile-first: base styles for phone, media queries for larger screens.
- Spacing: multiples of 1rem (16px); no arbitrary values.
- Font stack: `--font-body` for body copy, `--font-display` for headings.
- Colors: `--accent` (green) for primary CTAs, `--accent-2` (gold) for secondary, `--danger` (red) for destructive actions.
- Add new component styles in `style.css` following the section structure (comments with dashes).

### Form Handling
- Login and register forms currently have placeholders.
- When implementing: add `name` attributes to inputs, handle `request.form` in route handlers, validate server-side.
- Add client-side validation hints in JavaScript (check password match, email format).

### Testing Structure
- Tests should use `pytest-flask` fixtures: `client` (test client), `app` (app context).
- Database tests should use a separate SQLite database in memory or temp file.
- Example: `def test_landing(client): response = client.get('/'); assert response.status_code == 200`.

## Recent Changes

The landing page was redesigned to match mockups (most recent commit: `6c26139`). Features added:
- Hero section with "See How It Works" YouTube modal.
- Terms and Privacy Policy pages and routes.
- Consistent navbar/footer styling.

Placeholder routes for future steps are stubbed (logout, profile, expense CRUD).

## Key Files to Know

- **`app.py`** — All routes; start here for routing questions.
- **`templates/base.html`** — Layout and block structure; defines navbar, footer, CSS/JS inclusion.
- **`static/css/style.css`** — All visual styling; add components here.
- **`requirements.txt`** — Dependencies; update here when adding libraries.
- **`database/db.py`** — To be written; students implement DB interface.

## Next Steps (Student Learning Path)

1. **Step 1:** Write `database/db.py` with SQLite setup (get_db, init_db, seed_db).
2. **Step 2:** Add authentication endpoints (register, login with password hashing).
3. **Step 3:** Implement logout and session management.
4. **Step 4:** Add user profile page and editing.
5. **Steps 5–6:** Build expense model and data layer.
6. **Steps 7–9:** Implement add, edit, delete expense routes and forms.

Each step builds on the previous, with tests added incrementally.
