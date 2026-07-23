# Spec: Login and Logout

## Overview
Implements real authentication for Spendly. `GET /login` already renders a static form, but
submitting it does nothing, and `/logout` is still a placeholder string. This step wires
`login.html` up to a `POST /login` handler that verifies credentials against the `users` table
and starts a session, and turns `/logout` into a real route that ends the session. It builds
directly on the session infrastructure added in Step 2 (`app.secret_key`, `session` already
imported in `app.py`) and the `users` table from Step 1. Protecting other routes (e.g. requiring
login to view `/profile`) is out of scope here — `/profile` remains the Step 4 placeholder; this
step only covers establishing and ending a session.

## Depends on
- Step 1 — Database setup (`database/db.py`: `get_db()`, `users` table). Already complete.
- Step 2 — Registration (`app.py`: `app.secret_key`, `session`/`request`/`redirect`/`url_for`
  already imported; `users` table already gets rows via `POST /register`). Already complete.

## Routes
- `GET /login` — renders the login form (already implemented, unchanged) — public
- `POST /login` — validates credentials, starts a session, redirects to `/profile` — public
- `GET /logout` — clears the session, redirects to the landing page — logged-in (no error if
  called while already logged out — it should just redirect harmlessly)

## Database changes
No database changes. Authentication reads the existing `users` table (`email`, `password_hash`)
exactly as populated by `database/db.py` / `POST /register`.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change `<form method="POST" action="/login">` to
    `action="{{ url_for('login') }}"` per the project's `url_for()` convention; add
    `value="{{ email or '' }}"` to the email input so it survives a failed login (never
    repopulate the password input); the existing `{% if error %}` block gets driven by real data.
  - `templates/base.html` — nav currently always shows "Sign in" / "Get started" regardless of
    session state. Make it session-aware: when `session.get('user_id')` is set, show a "Log out"
    link (`{{ url_for('logout') }}`) instead of the "Sign in"/"Get started" links; when not
    logged in, keep the current nav exactly as-is.

## Files to change
- `app.py`:
  - Import `check_password_hash` from `werkzeug.security` (alongside the existing
    `generate_password_hash` import).
  - Change `login` view to `methods=["GET", "POST"]`:
    - On `GET`, render the form as today.
    - On `POST`, look up the user by email, verify the password with `check_password_hash`,
      and either set `session["user_id"]` and redirect to `/profile`, or re-render `login.html`
      with a generic error and the submitted email preserved.
  - Move `/logout` out of the placeholder block into the real `# --- Routes ---` section:
    clear the session (`session.clear()`) and redirect to `landing`. Remove the
    `# Placeholder routes` comment's implication that `/logout` is still stubbed — it no longer
    is, so keep that banner only around the routes still genuinely unimplemented
    (`/expenses/*`).
- `templates/login.html` — form action fix and email value preservation described above.
- `templates/base.html` — session-aware nav described above.

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only.
- Passwords hashed with werkzeug — verify with `check_password_hash`, never compare plaintext.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- Server-side validation:
  - `email` and `password` both required and non-empty after `.strip()`.
  - Look up the user by email; if no row exists, OR the password doesn't match the stored hash,
    show the **same** generic error either way (`"Invalid email or password."`) — never reveal
    whether the email itself was registered (avoids user enumeration).
- On any login failure, return the same `login.html` template with `error` populated and the
  submitted `email` preserved — do not redirect on failure.
- On success, set `session["user_id"]` to the authenticated user's id and redirect (302) to
  `/profile`, not render a template directly.
- `/logout` clears the session and redirects (302) to the landing page (`/`); it should not
  error if there was no active session to begin with.

## Definition of done
- [ ] `GET /login` still renders the empty form exactly as before (no error, no stray values).
- [ ] Submitting the correct email/password for an existing user (e.g. the seeded
      `demo@spendly.com` / `demo123`) sets the session and redirects to `/profile`.
- [ ] Submitting a wrong password for an existing email shows `"Invalid email or password."`
      and does not set a session.
- [ ] Submitting an email that doesn't exist in `users` shows the exact same
      `"Invalid email or password."` message (not a different one) and does not set a session.
- [ ] Submitting an empty email or empty password is rejected with a clear error and does not
      query the database with blank credentials.
- [ ] Re-submitting the login form after a failed attempt still shows the previously entered
      email (not blank), and the password field is empty.
- [ ] After a successful login, the nav (visible on any page) shows a "Log out" link instead of
      "Sign in"/"Get started".
- [ ] Visiting `/logout` clears the session and redirects to the landing page; the nav then
      reverts to showing "Sign in"/"Get started" again.
- [ ] App starts and runs without errors (`python app.py`).
