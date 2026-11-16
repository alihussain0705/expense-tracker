# Spec: Profile Page with Expense Overview

## Overview
The enhanced profile page allows logged-in users to view their account information (name, email, join date) and edit their name and email. Additionally, it displays a comprehensive expense overview including total spent, spending by category, recent transactions, and category breakdowns. This establishes the first user-specific dashboard in Spendly and demonstrates how to aggregate and visualize user expense data alongside profile management.

## Depends on
- **Step 1:** Database setup (users and expenses tables with proper schema)
- **Step 2:** User registration (users table populated with valid data)
- **Step 3:** Login and logout (session management via `session['user_id']`)
- **Expenses table:** Must exist with columns: id, user_id, amount, category, date, description, created_at

## Routes

- `GET /profile` — Display logged-in user's profile info (name, email, join date), edit form, and expense overview (total spent, category breakdown, recent transactions). Redirect to login if not authenticated. Access level: logged-in
- `POST /profile` — Handle profile edit form submission (name and/or email update). Validate inputs, check for duplicate email, update database, redirect to `/profile` on success. Access level: logged-in

## Database changes

No new tables or schema changes. Uses existing schema:
```
users (id, name, email, password_hash, created_at)
expenses (id, user_id, amount, category, date, description, created_at)
```

## Templates

**Create:**
- `templates/profile.html` — User profile page with three sections:
  1. Profile Info Display (name, email, join date)
  2. Expense Overview Summary (total spent, category breakdown with amounts, count of transactions)
  3. Edit Profile Form (name, email fields with validation messages)

**Modify:**
- `templates/base.html` — Possibly update navbar to show user initials or name when logged in (optional for Step 4, can be minimal)

## Files to change

- `app.py` — Replace placeholder `/profile` route with full implementation (GET and POST)
  - GET: fetch user data, calculate expense statistics (total, by category, recent transactions), format dates
  - POST: validate name/email, check uniqueness, update database

## Files to create

- `templates/profile.html` — New profile page template with expense overview
- `tests/test_profile.py` — Tests for profile viewing, editing, and expense data display (GET and POST)

## New dependencies

No new dependencies. Uses existing Flask, werkzeug, sqlite3.

## Rules for implementation

- **No SQLAlchemy or ORMs** — Use raw SQLite3 with parameterized queries only
- **Parameterized queries only** — All database queries must use `?` placeholders and pass values as tuples
- **Password hashing** — Do not allow password changes on this page (reserved for later step); this is name/email only
- **CSS variables** — Never hardcode hex values; use design tokens from `style.css` `:root`
- **Template inheritance** — `profile.html` must extend `base.html` with semantic blocks (title, content, scripts)
- **Session check** — Route must check `session.get('user_id')` and redirect to `/login` if not authenticated
- **Email uniqueness** — When updating email, check that new email is not already in use (except by current user)
- **Form validation** — Server-side validation for name (not empty, reasonable length), email (format, uniqueness)
- **Error handling** — Display validation errors inline on the profile form; use same error pattern as login/register
- **Database closure** — Always close database connection after query (or use context manager)
- **Expense aggregation** — Calculate totals and category breakdowns from expenses table using SQL GROUP BY, SUM, COUNT
- **Date formatting** — Format expense dates and join date for readable display (e.g., "November 15, 2026")
- **INR currency** — Display all expense amounts with ₹ symbol and proper formatting (e.g., ₹1,234.50)

## Definition of done

### Profile Management
- [ ] GET `/profile` displays logged-in user's name, email, and join date formatted as a readable date
- [ ] GET `/profile` redirects unauthenticated users to `/login`
- [ ] Profile page includes an edit form with fields for name and email
- [ ] POST `/profile` validates that name is not empty and at least 1 character
- [ ] POST `/profile` validates that email is in valid format (using same regex as registration)
- [ ] POST `/profile` prevents updating to an email already in use by another user
- [ ] POST `/profile` allows email update when new email is the same as current email (no-op update)
- [ ] POST `/profile` updates the `users` table and redirects back to `/profile` on success
- [ ] POST `/profile` displays validation errors inline on the form (error message, field highlighting optional)
- [ ] POST `/profile` handles database errors gracefully with user-friendly message

### Expense Overview
- [ ] GET `/profile` displays "Total Spent" amount as ₹X,XXX.XX format
- [ ] GET `/profile` displays count of total transactions
- [ ] GET `/profile` shows category breakdown with category name, amount spent in that category (₹ formatted), and transaction count
- [ ] Category breakdown includes all categories user has expenses in (Food, Transport, Bills, Health, Entertainment, Shopping, Other)
- [ ] GET `/profile` displays "Recent Transactions" section with at least last 5 transactions
- [ ] Recent transactions show: date, category, description, amount (₹ formatted)
- [ ] Transactions are sorted by date (most recent first)
- [ ] If user has no expenses, display "No expenses yet" instead of breakdown/transactions
- [ ] Expense data updates in real-time when new expenses are added (via future expense routes)

### Styling & UX
- [ ] Profile page is styled consistently with landing, login, and register pages (uses design tokens)
- [ ] Profile page is responsive on mobile (16px side gutter, no horizontal scroll)
- [ ] Expense overview section is visually distinct from profile info (card/panel layout)
- [ ] Category breakdown is clear and easy to scan (table or list format)
- [ ] Recent transactions are presented in a readable table or list

### Testing
- [ ] Tests pass: `pytest tests/test_profile.py -v`
- [ ] Tests cover: GET on logged-in user, GET on unauthenticated user, POST with valid update, POST with invalid name, POST with invalid email, POST with duplicate email
- [ ] Tests verify expense data is correctly aggregated and displayed
- [ ] Tests verify no expenses scenario displays appropriate message
- [ ] Tests verify currency formatting (₹) on all expense amounts

## Implementation Notes

### Expense Aggregation Queries

**Total spent and transaction count:**
```sql
SELECT 
    COALESCE(SUM(amount), 0) as total,
    COUNT(*) as transaction_count
FROM expenses
WHERE user_id = ?
```

**Category breakdown:**
```sql
SELECT 
    category,
    COALESCE(SUM(amount), 0) as category_total,
    COUNT(*) as category_count
FROM expenses
WHERE user_id = ?
GROUP BY category
ORDER BY category_total DESC
```

**Recent transactions (last 5):**
```sql
SELECT 
    id, date, category, description, amount
FROM expenses
WHERE user_id = ?
ORDER BY date DESC
LIMIT 5
```

### Currency Formatting (INR)
Use Python string formatting to display rupees with commas:
```python
def format_inr(amount):
    return f"₹{amount:,.2f}"
```

Example: `format_inr(1234.50)` → `₹1,234.50`

### Edge Cases
- User with no expenses: show "No expenses recorded yet" message
- Very large expense amounts: ensure formatting handles 5+ digit numbers correctly
- Decimal precision: store as REAL in DB, format to 2 decimals for display
- Date parsing: expenses stored as YYYY-MM-DD, format to readable "Month DD, YYYY"
