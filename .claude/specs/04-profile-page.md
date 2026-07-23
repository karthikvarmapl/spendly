# Spec: Profile Page

## Overview
Implements the real `/profile` page for Spendly. Right now `/profile` is a placeholder
string ("Profile page — coming in Step 4") that both `/register` and `/login` redirect
into after a successful session is created, so it is currently the first page a real
user would hit and is reachable by anyone regardless of login state. This step replaces
the stub with an actual page that displays the logged-in user's account details (name,
email, member-since date) and a lightweight summary of their recorded expenses (total
count and total spent), pulled from the `expenses` table that Step 1 already seeded. This
step also introduces Spendly's first login-required route: visiting `/profile` while
logged out must redirect to `/login` instead of rendering. No expense list, add, edit, or
delete UI is built here — that is Steps 7-9's job; this page only reads existing data.

## Depends on
- Step 1 — Database setup (`database/db.py`: `get_db()`, `users` and `expenses` tables,
  seeded demo data). Already complete.
- Step 2 — Registration (`app.py`: `session`, `app.secret_key`). Already complete.
- Step 3 — Login and Logout (`app.py`: session-aware nav in `base.html`, `/login` /
  `/logout` routes). Already complete.

## Routes
- `GET /profile` — renders the logged-in user's account info and expense summary —
  logged-in only. If `session.get('user_id')` is not set, redirect (302) to `/login`
  instead of rendering.

## Database changes
No database changes. This page only reads existing data:
- `users` (`name`, `email`, `created_at`) for the account info card.
- `expenses` (`amount`) aggregated per `user_id` for the summary (`COUNT(*)` and
  `SUM(amount)`), via a parameterised query scoped to `session['user_id']`.

## Templates
- **Create:** `templates/profile.html` — extends `base.html`; account info card (name,
  email, "member since" date formatted from `created_at`) plus a small stats section
  (total expenses recorded, total amount spent — showing 0 / $0.00 gracefully if the user
  has no expenses yet, avoiding a division/None error on `SUM()` returning `NULL`).
- **Modify:** `templates/base.html` — nav currently shows only a "Log out" link when
  logged in. Add a "My Profile" link (`{{ url_for('profile') }}`) next to it, shown only
  when `session.get('user_id')` is set; logged-out nav stays exactly as-is.

## Files to change
- `app.py`:
  - Move `profile` out of the `# --- Placeholder routes ---` block into the real
    `# --- Routes ---` section (it's no longer a stub). Keep the placeholder banner only
    around routes that are still genuinely unimplemented (`/expenses/*`).
  - Implement the `profile` view:
    - If `session.get('user_id')` is missing, `redirect(url_for('login'))`.
    - Otherwise, look up the user by id from `users`, run the aggregate query against
      `expenses` scoped to that `user_id`, and `render_template("profile.html", ...)`
      with the user's info and computed stats.
- `templates/base.html` — add the "My Profile" nav link described above.

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only.
- Passwords hashed with werkzeug (n/a for reads here, but no route should ever select or
  display `password_hash`).
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- `/profile` must check `session.get('user_id')` before querying the database; unauthenticated
  requests get a 302 redirect to `/login`, never a rendered page or a 500 from a failed lookup.
- The expense aggregate query must be scoped with `WHERE user_id = ?` — never compute stats
  across all users.
- Handle the zero-expenses case explicitly: `SUM(amount)` returns `NULL` with no rows, so
  coalesce it to `0` (e.g. `COALESCE(SUM(amount), 0)` in SQL, or a Python-side fallback)
  before formatting/display.

## Definition of done
- [ ] Visiting `/profile` while logged out redirects to `/login` (no page content leaks).
- [ ] Logging in as the seeded demo user (`demo@spendly.com` / `demo123`) and visiting
      `/profile` shows their name, email, and a member-since date.
- [ ] The stats section shows the correct count and total for the demo user's 8 seeded
      expenses (matches what's in `database/db.py`'s sample data).
- [ ] A newly registered user with no expenses sees `/profile` render without error, with
      the stats showing 0 expenses / $0.00 (no crash from `NULL` sums).
- [ ] The nav shows a "My Profile" link alongside "Log out" whenever logged in, and neither
      link appears when logged out.
- [ ] App starts and runs without errors (`python app.py`).
