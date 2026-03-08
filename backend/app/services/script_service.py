from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models import Script
from app.schemas import ScriptCreate, ScriptUpdate


class ScriptService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, script_id: int) -> Optional[Script]:
        return self.db.query(Script).filter(Script.id == script_id).first()

    def create(
        self,
        user_id: int,
        script_in: ScriptCreate,
        generated_content: str | None = None,
    ) -> Script:
        content = generated_content or script_in.content or f"Generated from keywords: {script_in.keywords}"
        is_generated = bool(generated_content)
        script = Script(
            user_id=user_id,
            title=script_in.title,
            content=content,
            output_type=script_in.output_type,
            parameters=script_in.parameters,
            status=1 if is_generated else 0,
        )

        self.db.add(script)
        self.db.commit()
        self.db.refresh(script)
        return script

    def update(self, script_id: int, script_in: ScriptUpdate) -> Script:
        script = self.get_by_id(script_id)
        if not script:
            raise NotFoundException(detail="Script not found")

        update_data = script_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(script, field, value)

        self.db.commit()
        self.db.refresh(script)
        return script

    def delete(self, script_id: int, user_id: int) -> bool:
        script = (
            self.db.query(Script)
            .filter(Script.id == script_id, Script.user_id == user_id)
            .first()
        )

        if not script:
            return False

        self.db.delete(script)
        self.db.commit()
        return True

    def get_user_scripts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: int | None = None,
    ) -> List[Script]:
        query = self.db.query(Script).filter(Script.user_id == user_id)
        if status is not None:
            query = query.filter(Script.status == status)
        return query.order_by(Script.created_at.desc()).offset(skip).limit(limit).all()

    def get_user_scripts_total(self, user_id: int, status: int | None = None) -> int:
        query = self.db.query(Script).filter(Script.user_id == user_id)
        if status is not None:
            query = query.filter(Script.status == status)
        return query.count()

    def mark_as_generated(self, script_id: int):
        script = self.get_by_id(script_id)
        if script:
            script.status = 1
            self.db.commit()
