from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models import Work
from app.core.exceptions import NotFoundException


class WorkService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, work_id: int) -> Optional[Work]:
        return self.db.query(Work).filter(Work.id == work_id).first()
    
    def create(
        self,
        user_id: int,
        work_type: str,
        file_url: str,
        task_id: int = None,
        title: str = None,
        thumbnail_url: str = None,
        parameters: dict = None
    ) -> Work:
        work = Work(
            user_id=user_id,
            task_id=task_id,
            work_type=work_type,
            title=title,
            file_url=file_url,
            thumbnail_url=thumbnail_url,
            parameters=parameters,
            is_public=0
        )
        
        self.db.add(work)
        self.db.commit()
        self.db.refresh(work)
        
        return work
    
    def update(self, work_id: int, **kwargs) -> Work:
        work = self.get_by_id(work_id)
        if not work:
            raise NotFoundException(detail="作品不存在")
        
        for key, value in kwargs.items():
            if hasattr(work, key):
                setattr(work, key, value)
        
        self.db.commit()
        self.db.refresh(work)
        return work
    
    def delete(self, work_id: int, user_id: int) -> bool:
        work = self.db.query(Work).filter(
            Work.id == work_id,
            Work.user_id == user_id
        ).first()
        
        if work:
            self.db.delete(work)
            self.db.commit()
            return True
        return False
    
    def get_user_works(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        work_type: str = None
    ) -> List[Work]:
        query = self.db.query(Work).filter(Work.user_id == user_id)
        
        if work_type:
            query = query.filter(Work.work_type == work_type)
        
        return query.order_by(Work.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_user_works_total(self, user_id: int, work_type: str = None) -> int:
        query = self.db.query(Work).filter(Work.user_id == user_id)
        
        if work_type:
            query = query.filter(Work.work_type == work_type)
        
        return query.count()
    
    def get_public_works(
        self,
        skip: int = 0,
        limit: int = 20,
        work_type: str = None
    ) -> List[Work]:
        query = self.db.query(Work).filter(Work.is_public == 1)
        
        if work_type:
            query = query.filter(Work.work_type == work_type)
        
        return query.order_by(Work.quality_score.desc(), Work.created_at.desc()).offset(skip).limit(limit).all()
    
    def set_public(self, work_id: int, is_public: int = 1):
        work = self.get_by_id(work_id)
        if work:
            work.is_public = is_public
            self.db.commit()
    
    def set_quality_score(self, work_id: int, score: int):
        work = self.get_by_id(work_id)
        if work:
            work.quality_score = score
            self.db.commit()
