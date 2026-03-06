"""客服工单服务"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.ticket import Ticket, TicketReply, Feedback


class TicketService:
    """工单服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_ticket(
        self,
        user_id: int,
        category: str,
        subject: str,
        content: str,
        priority: int = 1
    ) -> Ticket:
        """创建工单"""
        ticket_no = self._generate_ticket_no()

        ticket = Ticket(
            user_id=user_id,
            ticket_no=ticket_no,
            category=category,
            subject=subject,
            content=content,
            priority=priority,
            status=0
        )

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ticket

    def _generate_ticket_no(self) -> str:
        """生成工单编号"""
        from datetime import datetime
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = uuid.uuid4().hex[:6].upper()
        return f"TK{timestamp}{random_str}"

    def get_user_tickets(
        self,
        user_id: int,
        status: int = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Ticket]:
        """获取用户工单列表"""
        query = self.db.query(Ticket).filter(Ticket.user_id == user_id)

        if status is not None:
            query = query.filter(Ticket.status == status)

        return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()

    def get_ticket_by_no(self, ticket_no: str) -> Optional[Ticket]:
        """根据工单编号获取工单"""
        return self.db.query(Ticket).filter(Ticket.ticket_no == ticket_no).first()

    def add_reply(
        self,
        ticket_id: int,
        user_id: int,
        content: str,
        is_staff: int = 0,
        attachments: str = None
    ) -> TicketReply:
        """添加工单回复"""
        reply = TicketReply(
            ticket_id=ticket_id,
            user_id=user_id,
            is_staff=is_staff,
            content=content,
            attachments=attachments
        )

        self.db.add(reply)

        # 更新工单状态
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            if is_staff:
                ticket.status = 2  # 已回复
            else:
                if ticket.status == 2:
                    ticket.status = 1  # 处理中

        self.db.commit()
        self.db.refresh(reply)

        return reply

    def get_ticket_replies(self, ticket_id: int) -> List[TicketReply]:
        """获取工单回复列表"""
        return self.db.query(TicketReply).filter(
            TicketReply.ticket_id == ticket_id
        ).order_by(TicketReply.created_at).all()

    def update_ticket_status(
        self,
        ticket_id: int,
        status: int,
        assigned_to: int = None
    ) -> bool:
        """更新工单状态"""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            return False

        ticket.status = status

        if assigned_to is not None:
            ticket.assigned_to = assigned_to

        if status == 3:  # 已解决
            ticket.resolved_at = datetime.now()
        elif status == 4:  # 已关闭
            ticket.closed_at = datetime.now()

        self.db.commit()
        return True

    def get_all_tickets(
        self,
        status: int = None,
        priority: int = None,
        category: str = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Ticket]:
        """获取所有工单（管理员）"""
        query = self.db.query(Ticket)

        if status is not None:
            query = query.filter(Ticket.status == status)

        if priority is not None:
            query = query.filter(Ticket.priority == priority)

        if category:
            query = query.filter(Ticket.category == category)

        return query.order_by(Ticket.priority.desc(), Ticket.created_at).offset(skip).limit(limit).all()

    def get_pending_tickets(self, skip: int = 0, limit: int = 20) -> List[Ticket]:
        """获取待处理工单（管理员）"""
        return self.db.query(Ticket).filter(
            Ticket.status.in_([0, 1])
        ).order_by(Ticket.priority.desc(), Ticket.created_at).offset(skip).limit(limit).all()

    # 反馈管理
    def create_feedback(
        self,
        user_id: int,
        feedback_type: str,
        content: str,
        contact: str = None
    ) -> Feedback:
        """创建反馈"""
        feedback = Feedback(
            user_id=user_id,
            feedback_type=feedback_type,
            content=content,
            contact=contact,
            status=0
        )

        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)

        return feedback

    def get_user_feedbacks(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Feedback]:
        """获取用户反馈列表"""
        return self.db.query(Feedback).filter(
            Feedback.user_id == user_id
        ).order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()

    def reply_feedback(
        self,
        feedback_id: int,
        reply: str
    ) -> bool:
        """回复反馈（管理员）"""
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()

        if not feedback:
            return False

        feedback.reply = reply
        feedback.status = 1
        feedback.replied_at = datetime.now()

        self.db.commit()
        return True

    def get_all_feedbacks(
        self,
        status: int = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Feedback]:
        """获取所有反馈（管理员）"""
        query = self.db.query(Feedback)

        if status is not None:
            query = query.filter(Feedback.status == status)

        return query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
