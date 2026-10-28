# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

"Spendly" is a Flask-based expense tracker built as a step-by-step learning project. Routes and the database layer are intentionally scaffolded as placeholders with comments like `# Students will write this file in Step 1 — Database Setup` and `return "Add expense — coming in Step 7"`. When asked to implement a feature, check `app.py` and `database/db.py` for these markers — they indicate what's expected and at what stage of the build it belongs.

## Commands

Run from the repo root (`D:\Expense Tracker\expense-tracker\expense-tracker`).

```
# Activate the venv first (already created at ./venv)
venv\Scripts\activate          # PowerShell/cmd
source venv/Scripts/activate   # Git Bash

# Install dependencies
pip install -r requirements.txt

# Run the dev server (binds to port 5001, debug mode on)
python app.py

# Run tests
pytest
pytest path/to/test_file.py::test_name   # single test
```

There is no build step, linter, or frontend bundler — templates and static assets are served directly by Flask.

## Architecture

- **`app.py`** — single Flask app with all routes. No blueprints; everything lives in one file. Implemented routes (`/`, `/register`, `/login`, `/terms`, `/privacy`) render templates directly. Placeholder routes (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) currently return plain strings and are meant to be built out incrementally alongside the database layer.
- **`database/db.py`** — intended to hold `get_db()` (SQLite connection with `row_factory` and foreign keys enabled), `init_db()` (creates tables with `CREATE TABLE IF NOT EXISTS`), and `seed_db()` (sample dev data). Currently just a comment stub — not yet implemented.
- **`templates/`** — Jinja2 templates. `base.html` defines the shared shell (nav, footer, `{% block content %}`) that other pages extend. `landing.html`, `login.html`, `register.html`, `terms.html`, `privacy.html` are built out; templates for authenticated views (dashboard, expense list/add/edit) don't exist yet.
- **`static/css/style.css`** — shared site-wide styles (nav, footer, forms, base layout). **`static/css/landing.css`** — landing-page-specific styles, loaded only by `landing.html` via its `{% block head %}`.
- **`static/js/main.js`** — currently a single-line stub; no client-side logic yet.
- The SQLite DB file (`expense_tracker.db`) is gitignored and created at runtime by `init_db()` once that function is implemented — don't assume it exists on disk.

## Conventions observed in existing code

- Routes in `app.py` are grouped under comment banners (`# Routes`, `# Placeholder routes`) — keep new routes under the appropriate banner, or add a new one for a new concern (e.g. auth, expenses).
- Page titles and per-page `<head>`/`<script>` content are overridden via Jinja blocks (`{% block title %}`, `{% block head %}`, `{% block scripts %}`) rather than duplicating `base.html`.
