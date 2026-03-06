from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models import Task
from app.core.exceptions import NotFoundException
from app.utils import generate_task_no


class TaskService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def get_by_task_no(self, task_no: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.task_no == task_no).first()
    
    def create(
        self,
        user_id: int,
        task_type: str,
        parameters: dict,
        cost_amount: int = 0
    ) -> Task:
        task_no = generate_task_no()
        
        task = Task(
            user_id=user_id,
            task_no=task_no,
            task_type=task_type,
            parameters=parameters,
            cost_amount=cost_amount,
            status=0
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def update_status(
        self,
        task_id: int,
        status: int,
        progress: int = None,
        result_url: str = None,
        error_message: str = None
    ):
        task = self.get_by_id(task_id)
        if task:
            task.status = status
            if progress is not None:
                task.progress = progress
            if result_url:
                task.result_url = result_url
            if error_message:
                task.error_message = error_message
            if status == 2:
                task.completed_at = datetime.now()
            self.db.commit()
    
    def get_user_tasks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: int = None,
        task_type: str = None
    ) -> List[Task]:
        query = self.db.query(Task).filter(Task.user_id == user_id)
        
        if status is not None:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_user_tasks_total(
        self,
        user_id: int,
        status: int = None,
        task_type: str = None
    ) -> int:
        query = self.db.query(Task).filter(Task.user_id == user_id)
        
        if status is not None:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        return query.count()
    
    def get_pending_tasks(self, limit: int = 10) -> List[Task]:
        return self.db.query(Task).filter(
            Task.status == 0
        ).order_by(Task.created_at.asc()).limit(limit).all()
    
    def get_processing_tasks(self) -> List[Task]:
        return self.db.query(Task).filter(
            Task.status == 1
        ).all()
