from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db import crud

router = APIRouter(prefix="/dev", tags=["dev"])

class ActivateTestIn(BaseModel):
    token: str = Field(..., min_length=10, max_length=128)
    telegram_user_id: str = Field(..., min_length=3, max_length=32)

@router.post("/activate-test")
async def activate_test(payload: ActivateTestIn, db: AsyncSession = Depends(get_db)):
    """
    DEV-ONLY endpoint to test activation-token consumption without Telegram.
    Not mounted in production.
    """
    async with db.begin():
        user = await crud.consume_activation_and_activate_user(
            db,
            raw_token=payload.token,
            telegram_user_id=payload.telegram_user_id,
        )
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"user_id": user.id, "phone_number": user.phone_number, "is_active": user.is_active}
