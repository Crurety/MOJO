from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import AdminUser


class AdminUserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, admin_id: int) -> Optional[AdminUser]:
        return self.db.query(AdminUser).filter(AdminUser.id == admin_id).first()

    def get_by_account(self, account: str) -> Optional[AdminUser]:
        normalized = (account or "").strip()
        if not normalized:
            return None

        return (
            self.db.query(AdminUser)
            .filter(
                or_(
                    AdminUser.username == normalized,
                    AdminUser.email == normalized,
                )
            )
            .first()
        )

    def authenticate(self, account: str, password: str) -> Optional[AdminUser]:
        admin = self.get_by_account(account)
        if not admin:
            return None
        if not verify_password(password, admin.password):
            return None
        return admin

    def create(
        self,
        username: str,
        password: str,
        email: str | None = None,
        nickname: str | None = None,
        role: str = "admin",
    ) -> AdminUser:
        normalized_username = username.strip()
        existing = self.get_by_account(normalized_username)
        if existing:
            return existing

        admin = AdminUser(
            username=normalized_username,
            email=(email or None),
            password=get_password_hash(password),
            nickname=nickname,
            role=role,
            status=1,
        )
        self.db.add(admin)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existed = self.get_by_account(normalized_username)
            if existed:
                return existed
            raise
        self.db.refresh(admin)
        return admin

    def ensure_bootstrap_admin(self) -> Optional[AdminUser]:
        has_admin = self.db.query(AdminUser.id).first() is not None
        if has_admin:
            return None

        username = (settings.ADMIN_INIT_USERNAME or "").strip()
        password = settings.ADMIN_INIT_PASSWORD or ""
        if not username or not password:
            return None

        nickname = settings.ADMIN_INIT_NICKNAME or "Administrator"
        email = (settings.ADMIN_INIT_EMAIL or "").strip() or None
        return self.create(username=username, password=password, email=email, nickname=nickname)

    def update_last_login(self, admin_id: int, ip: str | None = None) -> None:
        admin = self.get_by_id(admin_id)
        if not admin:
            return
        admin.last_login_at = datetime.now()
        if ip:
            admin.last_login_ip = ip
        self.db.commit()

    def generate_token(self, admin_id: int) -> str:
        return create_access_token(subject=f"admin:{admin_id}")
