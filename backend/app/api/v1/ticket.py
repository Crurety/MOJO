"""Ticket and feedback API routes."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import User
from app.schemas import BaseResponse
from app.services.ticket_service import TicketService

router = APIRouter()


class TicketCreate(BaseModel):
    category: str
    subject: str
    content: str
    priority: int = 1


class TicketReplyCreate(BaseModel):
    content: str
    attachments: Optional[str] = None


class FeedbackCreate(BaseModel):
    feedback_type: str
    content: str
    contact: Optional[str] = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    ticket_no: str
    category: str
    subject: str
    content: str
    priority: int
    status: int
    assigned_to: Optional[int]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    created_at: datetime


class TicketReplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    user_id: int
    is_staff: int
    content: str
    attachments: Optional[str]
    created_at: datetime


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    feedback_type: str
    content: str
    contact: Optional[str]
    status: int
    reply: Optional[str]
    replied_at: Optional[datetime]
    created_at: datetime


@limiter.limit(RATE_LIMITS["general"])
@router.post("/tickets", response_model=BaseResponse)
def create_ticket(
    request: Request,
    ticket_in: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    ticket = ticket_service.create_ticket(
        user_id=current_user.id,
        category=ticket_in.category,
        subject=ticket_in.subject,
        content=ticket_in.content,
        priority=ticket_in.priority,
    )
    return BaseResponse(message="Ticket created", data={"ticket_no": ticket.ticket_no})


@limiter.limit(RATE_LIMITS["general"])
@router.get("/tickets", response_model=List[TicketResponse])
def get_tickets(
    request: Request,
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    tickets = ticket_service.get_user_tickets(current_user.id, status, skip, limit)
    return [TicketResponse.model_validate(t) for t in tickets]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/tickets/{ticket_no}", response_model=TicketResponse)
def get_ticket(
    request: Request,
    ticket_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    ticket = ticket_service.get_ticket_by_no(ticket_no)
    if not ticket or ticket.user_id != current_user.id:
        raise NotFoundException(detail="Ticket not found")
    return TicketResponse.model_validate(ticket)


@limiter.limit(RATE_LIMITS["general"])
@router.get("/tickets/{ticket_no}/replies", response_model=List[TicketReplyResponse])
def get_ticket_replies(
    request: Request,
    ticket_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    ticket = ticket_service.get_ticket_by_no(ticket_no)
    if not ticket or ticket.user_id != current_user.id:
        raise NotFoundException(detail="Ticket not found")

    replies = ticket_service.get_ticket_replies(ticket.id)
    return [TicketReplyResponse.model_validate(r) for r in replies]


@limiter.limit(RATE_LIMITS["general"])
@router.post("/tickets/{ticket_no}/replies", response_model=BaseResponse)
def add_ticket_reply(
    request: Request,
    ticket_no: str,
    reply_in: TicketReplyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    ticket = ticket_service.get_ticket_by_no(ticket_no)
    if not ticket or ticket.user_id != current_user.id:
        raise NotFoundException(detail="Ticket not found")

    reply = ticket_service.add_reply(
        ticket_id=ticket.id,
        user_id=current_user.id,
        content=reply_in.content,
        is_staff=0,
        attachments=reply_in.attachments,
    )
    return BaseResponse(message="Reply added", data={"reply_id": reply.id})


@limiter.limit(RATE_LIMITS["general"])
@router.post("/feedbacks", response_model=BaseResponse)
def create_feedback(
    request: Request,
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    feedback = ticket_service.create_feedback(
        user_id=current_user.id,
        feedback_type=feedback_in.feedback_type,
        content=feedback_in.content,
        contact=feedback_in.contact,
    )
    return BaseResponse(message="Feedback submitted", data={"feedback_id": feedback.id})


@limiter.limit(RATE_LIMITS["general"])
@router.get("/feedbacks", response_model=List[FeedbackResponse])
def get_feedbacks(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    feedbacks = ticket_service.get_user_feedbacks(current_user.id, skip, limit)
    return [FeedbackResponse.model_validate(f) for f in feedbacks]


@router.get("/admin/tickets")
def get_all_tickets(
    status: Optional[int] = Query(None),
    priority: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    tickets = ticket_service.get_all_tickets(status, priority, category, skip, limit)
    return {"items": [TicketResponse.model_validate(t) for t in tickets]}


@router.put("/admin/tickets/{ticket_id}/status", response_model=BaseResponse)
def update_ticket_status(
    ticket_id: int,
    status: int,
    assigned_to: Optional[int] = None,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    success = ticket_service.update_ticket_status(ticket_id, status, assigned_to)
    if not success:
        raise NotFoundException(detail="Ticket not found")
    return BaseResponse(message="Ticket status updated")


@router.post("/admin/tickets/{ticket_id}/replies", response_model=BaseResponse)
def admin_reply_ticket(
    ticket_id: int,
    reply_in: TicketReplyCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    reply = ticket_service.add_reply(
        ticket_id=ticket_id,
        user_id=current_admin.id,
        content=reply_in.content,
        is_staff=1,
        attachments=reply_in.attachments,
    )
    return BaseResponse(message="Reply added", data={"reply_id": reply.id})


@router.get("/admin/feedbacks")
def get_all_feedbacks(
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    feedbacks = ticket_service.get_all_feedbacks(status, skip, limit)
    return {"items": [FeedbackResponse.model_validate(f) for f in feedbacks]}


@router.put("/admin/feedbacks/{feedback_id}/reply", response_model=BaseResponse)
def reply_feedback(
    feedback_id: int,
    reply: str,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ticket_service = TicketService(db)
    success = ticket_service.reply_feedback(feedback_id, reply)
    if not success:
        raise NotFoundException(detail="Feedback not found")
    return BaseResponse(message="Feedback replied")
