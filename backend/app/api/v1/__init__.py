from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    content,
    coupon,
    help,
    invoice,
    notification,
    operation,
    payment,
    ticket,
    user,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(notification.router, prefix="/notification", tags=["notification"])
api_router.include_router(coupon.router, prefix="/coupon", tags=["coupon"])
api_router.include_router(help.router, prefix="/help", tags=["help"])
api_router.include_router(ticket.router, prefix="/ticket", tags=["ticket"])
api_router.include_router(invoice.router, prefix="/invoice", tags=["invoice"])
api_router.include_router(operation.router, prefix="/operation", tags=["operation"])
