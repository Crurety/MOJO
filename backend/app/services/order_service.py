from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models import Order, User
from app.core.exceptions import NotFoundException, BadRequestException
from app.utils import generate_order_no
from decimal import Decimal


class OrderService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()
    
    def get_by_order_no(self, order_no: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.order_no == order_no).first()
    
    def create(
        self,
        user_id: int,
        order_type: str,
        product_name: str,
        amount: Decimal,
        payment_method: str = None,
        remark: str = None
    ) -> Order:
        order_no = generate_order_no("O")
        
        order = Order(
            user_id=user_id,
            order_no=order_no,
            order_type=order_type,
            product_name=product_name,
            amount=amount,
            payment_method=payment_method,
            remark=remark,
            status=0
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def update_payment(
        self,
        order_no: str,
        payment_no: str,
        payment_method: str
    ) -> Order:
        order = self.get_by_order_no(order_no)
        if not order:
            raise NotFoundException(detail="订单不存在")
        
        if order.status != 0:
            raise BadRequestException(detail="订单状态不正确")
        
        order.payment_no = payment_no
        order.payment_method = payment_method
        order.status = 1
        order.paid_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def cancel(self, order_no: str) -> Order:
        order = self.get_by_order_no(order_no)
        if not order:
            raise NotFoundException(detail="订单不存在")
        
        if order.status != 0:
            raise BadRequestException(detail="订单状态不正确")
        
        order.status = 2
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    def get_user_orders(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: int = None,
        order_type: str = None
    ) -> List[Order]:
        query = self.db.query(Order).filter(Order.user_id == user_id)
        
        if status is not None:
            query = query.filter(Order.status == status)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_user_orders_total(
        self,
        user_id: int,
        status: int = None,
        order_type: str = None
    ) -> int:
        query = self.db.query(Order).filter(Order.user_id == user_id)
        
        if status is not None:
            query = query.filter(Order.status == status)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        
        return query.count()
    
    def get_all_orders(
        self,
        skip: int = 0,
        limit: int = 20,
        status: int = None,
        order_type: str = None
    ) -> List[Order]:
        query = self.db.query(Order)
        
        if status is not None:
            query = query.filter(Order.status == status)
        if order_type:
            query = query.filter(Order.order_type == order_type)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_total_revenue(self, start_date: datetime = None, end_date: datetime = None) -> Decimal:
        query = self.db.query(Order).filter(Order.status == 1)
        
        if start_date:
            query = query.filter(Order.paid_at >= start_date)
        if end_date:
            query = query.filter(Order.paid_at <= end_date)
        
        total = sum(order.amount for order in query.all())
        return Decimal(str(total))
