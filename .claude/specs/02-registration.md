# Spec: Registration

## Overview
This step implements account creation for Spendly. The `/register` route currently only renders `register.html` on GET; the form already posts to `/register` but there is no POST handler, no validation, and no database insert. This step wires the existing form up to the `users` table from Step 1 (Database Setup), so a visitor can create an account with a hashed password. It establishes the first real write path into the database and is the foundation for Step 3 (Login/Logout), which depends on users existing to authenticate against.

## Depends on
- Step 1 — Database Setup (`database/db.py` must have working `get_db()`, `init_db()`, `users` table)

## Routes
- `GET /register` — render the registration form (already implemented) — public
- `POST /register` — validate input, create the user, log them in, redirect to profile/dashboard — public

If no new routes: N/A — `/register` already exists; this step adds POST handling to it.

## Database changes
No database changes. The `users` table already has `name`, `email`, `password_hash`, `created_at` (see `database/db.py`), which is sufficient for registration. No new tables or columns needed.

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — add rendering for field-specific errors if needed (currently only has a generic `{% if error %}` block, which is sufficient); no structural changes required

## Files to change
- `app.py` — change `/register` route to accept `GET` and `POST`; add form validation, duplicate-email check, password hashing, insert, and session creation on success
- `database/db.py` — add a small helper if needed (e.g. `get_user_by_email(email)`), using parameterized queries against the existing `users` table

## Files to create
None

## New dependencies
No new dependencies. Use `werkzeug.security.generate_password_hash` (already used in `seed_db()`) and Flask's built-in `session`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`, verified later with `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate required fields (name, email, password) server-side even though the form has `required` attributes client-side
- Enforce a minimum password length (8 characters, matching the placeholder text in `register.html`)
- Reject registration if the email already exists (catch the `UNIQUE` constraint or pre-check), showing the existing `auth-error` block with a clear message
- On success, store the new user's id in `session` and redirect (do not re-render a success page)
- Never store or log plaintext passwords

## Definition of done
- [ ] Submitting the register form with valid name/email/password creates a row in `users` with a hashed password (verify via sqlite or a quick script)
- [ ] Submitting with an email that already exists shows an error on the page and does not create a duplicate row
- [ ] Submitting with a missing field or password under 8 characters shows an error and does not create a row
- [ ] On successful registration, the session contains the new user's id and the browser is redirected away from `/register`
- [ ] GET `/register` still renders the form as before
- [ ] App starts and runs with no errors (`python app.py`)
