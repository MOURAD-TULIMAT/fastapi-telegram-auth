# FastAPI Telegram Auth Service (WIP)

Auth microservice built with **FastAPI** + **async SQLAlchemy (MySQL)**. Telegram verification flow will be added next.

## Implemented
- `GET /v1/health` — service health
- `GET /v1/db/health` — DB connectivity (`SELECT 1`)
- `POST /v1/auth/register` — creates/overwrites **inactive** user + issues **activation token**
  - User PK: `id` (UUID string)
  - `phone_number`: **unique + indexed**
  - Overwrite inactive user only if `updated_at` older than `INACTIVE_OVERWRITE_AFTER_SECONDS`
  - Requires `TELEGRAM_BOT_USERNAME` to return a deep link

Swagger: `http://127.0.0.1:8000/docs`

## Run (dev)
```bash
docker compose up -d
py -m uvicorn app.main:app --reload
```

## Env (minimum)
- `DATABASE_URL` (MySQL async)
- `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE` (docker)
- `TELEGRAM_BOT_USERNAME`

## TODO
- Retry activation endpoint
- Activation token validation/consumption
- Login (JWT) + password hashing
- Forgot/reset/change password endpoints
- Telegram webhook + `/start` + contact verification
- Admin broadcast (`/podcast`)
- Add Alembic migrations + tests

