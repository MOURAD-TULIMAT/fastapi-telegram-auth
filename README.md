# FastAPI Telegram Auth Service (WIP)

A small **authentication microservice** that lets users register with a **phone number** and confirms ownership of that phone number via a **Telegram bot** (by asking the user to send their Telegram contact card).  
It is designed to be embedded into any product (mobile/web/backend) that needs “phone-based signup + Telegram verification” as a separate microservice.

## How you integrate this into your product

### Typical client flow (your app / frontend)
1) **Collect registration data** (phone, username, first/last name, optional email).
2) Call `POST /v1/auth/register`.
3) You receive a **Telegram deep link** like:
   `https://t.me/<BOT_USERNAME>?start=<token>`
4) Show the deep link to the user (button / “Open Telegram”).
5) User taps the link → bot asks them to **send contact card** → account becomes **active**.

### Retry activation
If the user lost the link or didn’t finish activation:
1) Call `POST /v1/auth/retry-activation` with phone only.
2) You receive a **new deep link**.

### What this service guarantees
- Users are created as **inactive** until they confirm the phone number.
- Activation is finalized only after:
  - a valid activation token was used in `/start <token>`, and
  - the user sends a contact card where the phone matches the registered phone.

## Implemented (current)

### API
- `GET /v1/health` — service health
- `GET /v1/db/health` — DB connectivity (`SELECT 1`)
- `POST /v1/auth/register`
  - Creates/overwrites **inactive** user (overwrite window)
  - Issues **activation token** (raw token returned; **hash stored** in DB)
  - Returns Telegram deep link: `https://t.me/<BOT>?start=<token>`
- `POST /v1/auth/retry-activation`
  - Phone-only
  - Requires user exists and is inactive
  - Re-issues activation token (single active token per user)

### Telegram bot (local dev: long polling)
- `/start`
  - No token → sends registration URL button
  - Invalid/expired token → sends Register + Retry buttons
  - Valid token → binds `telegram_user_id` to the inactive user (pending) and asks for contact card
- Contact card handler
  - Verifies sender is sending their own contact
  - Finds user by `telegram_user_id`, validates phone match
  - Consumes activation token and activates the user

### Dev-only endpoint (testing helper)
- `POST /v1/dev/activate-test` (only when `ENVIRONMENT=dev`)
  - Tests token consumption + activation without Telegram
  - Not mounted in production

### Security practices already applied
- User PK is UUID string (`String(36)`); `phone_number` is **unique + indexed**
- Tokens are **not stored in plain text** (only SHA-256 hash; optional pepper)
- Input validation at API boundary (phone normalization, `EmailStr` when provided)
- Single usable activation token per user (old tokens removed on register/retry)

Swagger: `http://127.0.0.1:8000/docs`

## Run (dev)

### 1) Start MySQL
```bash
docker compose up -d
```

### 2) Run the API
```bash
py -m uvicorn app.main:app --reload
```

### 3) Run the Telegram bot (polling)
```bash
python run_bot.py
```

## Environment variables (minimum)
- `ENVIRONMENT` (`dev` or `prod`)
- `DATABASE_URL`
- `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `WEB_APP_BASE_URL`, `WEB_APP_REGISTER_PATH`, `WEB_APP_RETRY_ACTIVATION_PATH`
- `TOKEN_HASH_PEPPER` (optional)

## TODO (next)

### Telegram
- Admin broadcast: `/podcast` (admin only) → broadcast next message to active users
- Improve UX messages/buttons for mismatch cases:
  - wrong Telegram account
  - wrong phone number
  - forward activation link

### Password flows
- Forgot password (by phone or by userId if logged in) → reset token → Telegram link
- Reset password (consume token, set password hash)
- Change password (authenticated + optional bot shortcut)

### Auth
- Login endpoint + JWT access tokens
- Password hashing (`bcrypt`), rate limiting on sensitive endpoints

### Engineering
- Add Alembic migrations (stop relying on `create_all()`)
- Tests (pytest), CI checks, linting/formatting
- Webhook mode + secret header validation (when deploying)
