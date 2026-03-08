from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.models import AdminUser, User

security = HTTPBearer(auto_error=False)
optional_security = HTTPBearer(auto_error=False)


def _parse_subject_from_token(token: str) -> str:
    subject = decode_access_token(token)
    if not subject:
        raise UnauthorizedException(detail="Invalid token")
    return subject


def _parse_user_id_from_subject(subject: str) -> int:
    try:
        return int(subject)
    except (TypeError, ValueError):
        raise UnauthorizedException(detail="Invalid token subject")


def _parse_admin_id_from_subject(subject: str) -> int:
    if not subject.startswith("admin:"):
        raise UnauthorizedException(detail="Admin token required")

    try:
        return int(subject.split(":", 1)[1])
    except (TypeError, ValueError):
        raise UnauthorizedException(detail="Invalid admin token subject")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedException(detail="Not authenticated")

    subject = _parse_subject_from_token(credentials.credentials)
    user_id = _parse_user_id_from_subject(subject)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException(detail="User not found")

    if user.status != 1:
        raise UnauthorizedException(detail="User is disabled")

    return user


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AdminUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedException(detail="Not authenticated")

    subject = _parse_subject_from_token(credentials.credentials)
    admin_id = _parse_admin_id_from_subject(subject)

    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        raise UnauthorizedException(detail="Admin not found")

    if admin.status != 1:
        raise UnauthorizedException(detail="Admin is disabled")

    return admin


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None

    try:
        subject = _parse_subject_from_token(credentials.credentials)
        user_id = _parse_user_id_from_subject(subject)
    except UnauthorizedException:
        return None

    return db.query(User).filter(User.id == user_id).first()
