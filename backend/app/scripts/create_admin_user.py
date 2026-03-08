from __future__ import annotations

import argparse

from app.core.database import SessionLocal
from app.services.admin_user_service import AdminUserService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create backend admin account")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--email", default=None, help="Admin email")
    parser.add_argument("--nickname", default="Administrator", help="Admin nickname")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        service = AdminUserService(db)
        existing = service.get_by_account(args.username)
        if existing:
            print(f"Admin already exists: {args.username} (id={existing.id})")
            return

        admin = service.create(
            username=args.username,
            password=args.password,
            email=args.email,
            nickname=args.nickname,
        )
        print(f"Admin created: username={admin.username}, id={admin.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
