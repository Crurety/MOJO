from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.services import MessageService


@celery_app.task
def send_welcome_message(user_id: int):
    db = SessionLocal()
    try:
        message_service = MessageService(db)
        
        message_service.create(
            user_id=user_id,
            title="欢迎加入AI创作平台",
            content="感谢您注册AI创作平台，开始您的创作之旅吧！",
            message_type="system"
        )
        
        return {"status": "success"}
    
    finally:
        db.close()


@celery_app.task
def send_payment_success_notification(user_id: int, order_no: str, product_name: str):
    db = SessionLocal()
    try:
        message_service = MessageService(db)
        
        message_service.create(
            user_id=user_id,
            title="支付成功",
            content=f"您的订单 {order_no} 支付成功，商品：{product_name}",
            message_type="system",
            link=f"/account/orders/{order_no}"
        )
        
        return {"status": "success"}
    
    finally:
        db.close()


@celery_app.task
def send_permission_expiring_notification(user_id: int, permission_type: str, days_left: int):
    db = SessionLocal()
    try:
        message_service = MessageService(db)
        
        message_service.create(
            user_id=user_id,
            title="权限即将到期",
            content=f"您的{permission_type}权限将在{days_left}天后到期，请及时续费。",
            message_type="system",
            link="/pricing"
        )
        
        return {"status": "success"}
    
    finally:
        db.close()
