# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This is **Spendly**, a Flask expense tracker built incrementally as a step-by-step learning exercise. Most backend logic is intentionally stubbed out with `# Students will implement...` / `coming in Step N` placeholders — do not assume features exist just because a route or file is present. Check the actual contents before building on top of something.

Currently implemented: the landing, register, and login page templates/routes only (rendering static HTML, no real auth or persistence yet). Everything else (sessions, database, CRUD for expenses) is a placeholder awaiting implementation.

## Setup and running

The project uses a local venv (`venv/`) with dependencies in `requirements.txt` (Flask 3.1.3, Werkzeug, pytest, pytest-flask).

```bash
source venv/bin/activate
python app.py          # runs on http://127.0.0.1:5001 (debug=True)
```

Always activate the venv first — `python3`/`pip` outside it point at the system Python, which does not have Flask installed. If dependencies are missing inside the venv, run `pip install -r requirements.txt` after activating.

There is no test suite yet despite pytest/pytest-flask being listed as dependencies — they're there for when tests get added.

## Architecture

- `app.py` — single Flask app with all routes defined directly on it (no blueprints). Routes fall into two groups: implemented pages (`/`, `/register`, `/login`) and stub routes for future steps (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`), which currently just return a plain string placeholder.
- `database/db.py` — will hold `get_db()` (SQLite connection with `row_factory` + foreign keys on), `init_db()` (`CREATE TABLE IF NOT EXISTS` schema), and `seed_db()` (dev sample data). Not yet implemented — this is the Step 1 deliverable in the course this project follows.
- `templates/` — Jinja2 templates. `base.html` defines the shared layout (nav, footer, font/CSS includes) via `{% block %}`s; page templates (`landing.html`, `login.html`, `register.html`) extend it.
- `static/css/style.css` — all styling lives in one file, driven by CSS custom properties defined in `:root` (colors, fonts, radii). Follow this variable-based approach rather than hardcoding values when adding styles.
- `static/js/main.js` — empty placeholder; JS gets added per-feature as steps are implemented.
- SQLite database file (`expense_tracker.db`) is gitignored and created at runtime — never commit it.

## Conventions from existing code

- Routes in `app.py` are grouped under `# --- Routes ---` / `# --- Placeholder routes ---` comment banners — keep new routes organized the same way, and remove the "placeholder" banner/comment for a route once it's actually implemented.
- Templates use `url_for()` for all internal links (nav, footer, forms) rather than hardcoded paths.
