from __future__ import annotations

import hashlib
from uuid import uuid4

from app.core.config import settings


def new_raw_token() -> str:
    # 32 hex chars, random enough for one-time activation/reset
    return uuid4().hex


def token_hash(raw_token: str) -> str:
    # Optional pepper (recommended in prod); does not change external flow
    pepper = (getattr(settings, "TOKEN_HASH_PEPPER", "") or "").encode("utf-8")
    return hashlib.sha256(pepper + raw_token.encode("utf-8")).hexdigest()
