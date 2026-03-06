import os
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.models import User

security = HTTPBearer(auto_error=False)
optional_security = HTTPBearer(auto_error=False)


def _parse_user_id_from_token(token: str) -> int:
    subject = decode_access_token(token)
    if not subject:
        raise UnauthorizedException(detail="Invalid token")

    try:
        return int(subject)
    except (TypeError, ValueError):
        raise UnauthorizedException(detail="Invalid token subject")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedException(detail="Not authenticated")

    user_id = _parse_user_id_from_token(credentials.credentials)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException(detail="User not found")

    if user.status != 1:
        raise UnauthorizedException(detail="User is disabled")

    return user


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user = get_current_user(credentials=credentials, db=db)

    # In tests, use explicit admin account identity instead of .env ADMIN_USER_IDS.
    admin_ids = set() if os.getenv("TESTING") else set(settings.ADMIN_USER_IDS or [])
    email = (user.email or "").lower()
    is_admin_email = email.startswith("admin@")

    if user.id not in admin_ids and not is_admin_email:
        raise UnauthorizedException(detail="Admin permission required")

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None

    try:
        user_id = _parse_user_id_from_token(credentials.credentials)
    except UnauthorizedException:
        return None

    return db.query(User).filter(User.id == user_id).first()
