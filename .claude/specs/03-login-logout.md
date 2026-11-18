# Spec: Login and Logout

## Overview
This step implements authentication for Spendly. Registration (Step 2) can create users, but there is no way to sign in yet: `/login` only renders `login.html` on GET with no POST handler, and `/logout` is a placeholder string. This step wires the existing login form to check credentials against the `users` table, establishes a Flask session on success, and implements `/logout` to clear it. This is the foundation for Step 4 (Profile) and all later authenticated views (dashboard, expense list/add/edit), which need to know who is signed in.

## Depends on
- Step 1 — Database Setup (`users` table, `get_db()`)
- Step 2 — Registration (users must exist to log in; reuses `get_user_by_email()`)

## Routes
- `GET /login` — render the login form (already implemented) — public
- `POST /login` — verify credentials, start session, redirect to `/profile` — public
- `GET /logout` — clear the session, redirect to `/login` — logged-in

## Database changes
No database changes. `users.password_hash` already exists and is sufficient to verify credentials with `werkzeug.security.check_password_hash`.

## Templates
- **Create:** none
- **Modify:** none — `login.html` already has the `{% if error %}` block and posts the right field names (`email`, `password`) to `/login`

## Files to change
- `app.py` — add `app.secret_key` config; change `/login` to accept `GET` and `POST`; implement `/logout` to clear the session instead of returning a placeholder string
- No changes needed to `database/db.py` — `get_user_by_email()` from Step 2 is reused as-is

## Files to create
None

## New dependencies
No new dependencies. Use `werkzeug.security.check_password_hash` and Flask's built-in `session`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (verify with `check_password_hash`, never compare plaintext)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Set `app.secret_key` (a fixed development value is fine at this stage; do not hardcode it inline next to route logic — define it near app setup)
- On successful login, store the user's `id` in `session` (e.g. `session["user_id"]`)
- On `POST /login` with invalid email or wrong password, show a single generic error ("Invalid email or password.") — do not reveal whether the email exists, to avoid leaking which emails are registered
- `/logout` must clear the session (`session.clear()`) and redirect to `/login`
- Never store or log plaintext passwords

## Definition of done
- [ ] GET `/login` still renders the form as before
- [ ] Submitting valid credentials for an existing user (e.g. the seeded `demo@spendly.com` / `demo123`) redirects to `/profile` and sets `session["user_id"]`
- [ ] Submitting a wrong password for an existing email shows a generic invalid-credentials error and does not set the session
- [ ] Submitting an email that doesn't exist shows the same generic error (no distinct message)
- [ ] Visiting `/logout` after logging in clears the session and redirects to `/login`
- [ ] App starts and runs with no errors (`python app.py`)
