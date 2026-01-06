from pydantic import BaseModel, Field, EmailStr, field_validator
from app.core.phone import normalize_phone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.db import crud

router = APIRouter(prefix="/auth")

class RegisterIn(BaseModel):
    phone_number: str = Field(..., min_length=5, max_length=32)
    username: str = Field(..., min_length=3, max_length=64)
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    email: str | None = None
    @field_validator("phone_number")
    @classmethod
    def _normalize_phone(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("phone_number is required")
        return normalize_phone(v)
    @field_validator("username", "first_name", "last_name")
    @classmethod
    def _strip_names(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("field is required")
        return v
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr | None):
        if v is None:
            return None
        # Optional: normalize
        return EmailStr(str(v).strip().lower())

@router.post("/register")
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    try:
        async with db.begin():
            user = await crud.upsert_inactive_user_for_registration(
                db,
                phone_number=payload.phone_number,
                username=payload.username,
                first_name=payload.first_name,
                last_name=payload.last_name,
                email=payload.email,
            )
            await db.flush()
            tokenInfo, token = await crud.create_activation_token(db, user.id)
    except ValueError as e:
        if str(e) == "USER_ALREADY_ACTIVE":
            raise HTTPException(status_code=409, detail="User already active")
        if str(e) == "REGISTRATION_RECENTLY_CREATED":
            raise HTTPException(status_code=409, detail="Registration initiated recently. Use retry activation.")
        raise

    if not settings.TELEGRAM_BOT_USERNAME:
        raise HTTPException(status_code=500, detail="Telegram bot username not configured")

    telegram_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}"
    return {
        "user_id": user.id,
        "phone_number": user.phone_number,
        "is_active": user.is_active,
        "activation_token": token,
        "telegram_link": telegram_link,
        "expires_at": tokenInfo.expires_at.isoformat(),
    }
