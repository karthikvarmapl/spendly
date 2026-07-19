# Spec: Registration

## Overview
Implements real account creation for Spendly. Currently `/register` only renders a static
template — submitting the form does nothing. This step wires the existing `register.html`
form up to a `POST /register` handler that validates input, hashes the password, inserts a
new row into `users`, starts a logged-in session, and redirects into the app. It builds
directly on the Step 1 database layer (`database/db.py`), which is already implemented.

## Depends on
- Step 1 — Database setup (`database/db.py`: `get_db()`, `init_db()`, `users` table). Already complete.

## Routes
- `GET /register` — renders the registration form (already implemented, unchanged) — public
- `POST /register` — validates and creates a new user, starts a session, redirects to `/profile` — public

## Database changes
No database changes. The `users` table (`id`, `name`, `email`, `password_hash`, `created_at`)
already supports registration as defined in `database/db.py`.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — change `<form method="POST" action="/register">` to
  `action="{{ url_for('register') }}"` per the project's `url_for()` convention; the existing
  `{% if error %}` block and field `value=` attributes will be driven by real data from the route
  instead of sitting unused.

## Files to change
- `app.py`:
  - Add `app.secret_key` configuration (required for session support).
  - Import `request`, `redirect`, `url_for`, `session` from `flask`.
  - Import `get_db` usage for inserts (already imported) and `generate_password_hash` from
    `werkzeug.security`.
  - Change `register` view to accept `methods=["GET", "POST"]`:
    - On `GET`, render the form as today.
    - On `POST`, validate input, insert the user, set `session["user_id"]`, redirect to `/profile`.
    - On validation failure, re-render `register.html` with `error` set and the submitted
      `name`/`email` preserved in the form fields.
- `templates/register.html` — form action fix described above.

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs.
- Parameterised queries only.
- Passwords hashed with werkzeug (`generate_password_hash` / never store plaintext).
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`.
- Validate server-side (do not trust the HTML `required`/`type=email` attributes alone):
  - `name`, `email`, `password` all required and non-empty after `.strip()`.
  - `password` must be at least 8 characters (matches the form's placeholder copy).
  - `email` must not already exist in `users` — check before insert (or catch the
    `sqlite3.IntegrityError` from the `UNIQUE` constraint) and show a clear error either way.
- On any validation error, return the same `register.html` template with `error` populated —
  do not redirect on failure, and do not lose the user's `name`/`email` input.
- On success, set `session["user_id"]` to the new user's id and redirect (302) to `/profile`,
  not render a template directly, so a page refresh doesn't resubmit the form.

## Definition of done
- [ ] `GET /register` still renders the empty form exactly as before.
- [ ] Submitting valid name/email/password creates exactly one new row in `users` with a
      hashed (not plaintext) password.
- [ ] Submitting with an email that already exists shows an error and creates no new row.
- [ ] Submitting with a password under 8 characters shows an error and creates no new row.
- [ ] Submitting with any empty field shows an error and creates no new row.
- [ ] After a successful registration, the browser is redirected to `/profile` and the session
      contains the new user's id.
- [ ] Re-submitting the form after a validation error still shows the previously entered name
      and email (not a blank form).
- [ ] App starts and runs without errors (`python app.py`).
