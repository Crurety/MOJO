"""Invoice API routes."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models import User
from app.schemas import BaseResponse
from app.services.invoice_service import InvoiceService

router = APIRouter()


class RealNameSubmit(BaseModel):
    real_name: str
    id_card: str
    id_card_front: Optional[str] = None
    id_card_back: Optional[str] = None


class RealNameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    real_name: str
    id_card: str
    id_card_front: Optional[str]
    id_card_back: Optional[str]
    status: int
    reject_reason: Optional[str]
    verified_at: Optional[datetime]


class InvoiceCreate(BaseModel):
    order_id: Optional[int] = None
    invoice_type: str = Field(..., description="normal/special")
    invoice_title: str
    tax_no: str
    amount: Decimal
    recipient_name: str
    recipient_phone: str
    recipient_address: str
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    order_id: Optional[int]
    invoice_no: str
    invoice_type: str
    invoice_title: str
    tax_no: str
    amount: Decimal
    company_address: Optional[str]
    company_phone: Optional[str]
    bank_name: Optional[str]
    bank_account: Optional[str]
    recipient_name: str
    recipient_phone: str
    recipient_address: str
    status: int
    reject_reason: Optional[str]
    invoice_url: Optional[str]
    tracking_no: Optional[str]
    issued_at: Optional[datetime]
    mailed_at: Optional[datetime]
    created_at: datetime


@limiter.limit(RATE_LIMITS["general"])
@router.post("/real-name/submit", response_model=BaseResponse)
def submit_real_name(
    real_name_in: RealNameSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    real_name = invoice_service.submit_real_name(
        user_id=current_user.id,
        real_name=real_name_in.real_name,
        id_card=real_name_in.id_card,
        id_card_front=real_name_in.id_card_front,
        id_card_back=real_name_in.id_card_back,
    )
    return BaseResponse(message="Real-name submitted", data={"record_id": real_name.id})


@limiter.limit(RATE_LIMITS["general"])
@router.get("/real-name/status")
def get_real_name_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    info = invoice_service.get_real_name_status(current_user.id)
    if not info:
        return {"status": None}
    return RealNameResponse.model_validate(info)


@limiter.limit(RATE_LIMITS["general"])
@router.post("/invoices", response_model=BaseResponse)
def create_invoice(
    invoice_in: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    invoice = invoice_service.create_invoice(
        user_id=current_user.id,
        order_id=invoice_in.order_id or 0,
        invoice_type=invoice_in.invoice_type,
        invoice_title=invoice_in.invoice_title,
        tax_no=invoice_in.tax_no,
        amount=invoice_in.amount,
        recipient_name=invoice_in.recipient_name,
        recipient_phone=invoice_in.recipient_phone,
        recipient_address=invoice_in.recipient_address,
        company_address=invoice_in.company_address,
        company_phone=invoice_in.company_phone,
        bank_name=invoice_in.bank_name,
        bank_account=invoice_in.bank_account,
    )
    return BaseResponse(message="Invoice request created", data={"invoice_no": invoice.invoice_no})


@limiter.limit(RATE_LIMITS["general"])
@router.get("/invoices", response_model=List[InvoiceResponse])
def get_my_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    invoices = invoice_service.get_user_invoices(current_user.id, skip, limit)
    return [InvoiceResponse.model_validate(inv) for inv in invoices]


@limiter.limit(RATE_LIMITS["general"])
@router.get("/invoices/{invoice_no}", response_model=InvoiceResponse)
def get_invoice(
    invoice_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_no(invoice_no)
    if not invoice or invoice.user_id != current_user.id:
        raise NotFoundException(detail="Invoice not found")
    return InvoiceResponse.model_validate(invoice)


@router.get("/admin/real-names")
def get_pending_real_names(
    status: Optional[int] = Query(0),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    from app.models.invoice import UserRealName

    query = db.query(UserRealName)
    if status is not None:
        query = query.filter(UserRealName.status == status)

    items = query.order_by(UserRealName.created_at).offset(skip).limit(limit).all()
    return {
        "items": [
            {
                "id": rn.id,
                "user_id": rn.user_id,
                "real_name": rn.real_name,
                "id_card": rn.id_card,
                "status": rn.status,
                "created_at": rn.created_at,
            }
            for rn in items
        ]
    }


@router.put("/admin/real-names/{user_id}/verify", response_model=BaseResponse)
def verify_real_name(
    user_id: int,
    approved: bool,
    reject_reason: Optional[str] = None,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    success = invoice_service.verify_real_name(user_id, approved, reject_reason)
    if not success:
        raise NotFoundException(detail="Real-name record not found")
    return BaseResponse(message="Real-name verified")


@router.get("/admin/invoices")
def get_all_invoices(
    status: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    invoices = invoice_service.get_all_invoices(status, skip, limit)
    return {"items": [InvoiceResponse.model_validate(inv) for inv in invoices]}


@router.put("/admin/invoices/{invoice_id}/status", response_model=BaseResponse)
def update_invoice_status(
    invoice_id: int,
    status: int,
    invoice_url: Optional[str] = None,
    tracking_no: Optional[str] = None,
    reject_reason: Optional[str] = None,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    invoice_service = InvoiceService(db)
    success = invoice_service.update_invoice_status(
        invoice_id,
        status,
        invoice_url,
        tracking_no,
        reject_reason,
    )
    if not success:
        raise NotFoundException(detail="Invoice not found")
    return BaseResponse(message="Invoice status updated")
