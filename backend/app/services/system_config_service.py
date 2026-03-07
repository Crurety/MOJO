from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models import SystemConfig


class SystemConfigService:
    def __init__(self, db: Session):
        self.db = db

    def get_values(self, keys: list[str]) -> Dict[str, str]:
        if not keys:
            return {}

        rows = (
            self.db.query(SystemConfig)
            .filter(SystemConfig.config_key.in_(keys))
            .all()
        )
        return {row.config_key: row.config_value for row in rows}

    def set_values(
        self, values: Dict[str, str], descriptions: Optional[Dict[str, str]] = None
    ) -> None:
        if not values:
            return

        keys = list(values.keys())
        existing = (
            self.db.query(SystemConfig)
            .filter(SystemConfig.config_key.in_(keys))
            .all()
        )
        existing_map = {row.config_key: row for row in existing}

        for key, value in values.items():
            row = existing_map.get(key)
            description = descriptions.get(key) if descriptions else None
            if row:
                row.config_value = value
                if description is not None:
                    row.description = description
                continue

            self.db.add(
                SystemConfig(
                    config_key=key,
                    config_value=value,
                    description=description,
                )
            )

        self.db.commit()

