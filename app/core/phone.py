import re
from typing import Optional
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException

from app.core.config import settings

def normalize_phone(phone: str, default_region: Optional[str] = None) -> str:
    phone = (phone or "").strip()
    if not phone:
        return phone

    region = (default_region or getattr(settings, "DEFAULT_PHONE_REGION", "AE")).strip() or "AE"
    try:
        num = phonenumbers.parse(phone, region)
        if phonenumbers.is_possible_number(num) and phonenumbers.is_valid_number(num):
            return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        pass

    has_plus = phone.startswith("+")
    digits = re.sub(r"\D+", "", phone)
    return f"+{digits}" if has_plus else digits
