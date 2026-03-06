from typing import Dict, Any, Optional
from app.payment.wechat import wechat_pay_service
from app.payment.alipay import alipay_service
from app.payment.unionpay import unionpay_service


class PaymentService:
    def __init__(self):
        self.wechat = wechat_pay_service
        self.alipay = alipay_service
        self.unionpay = unionpay_service
    
    async def create_payment(
        self,
        payment_method: str,
        order_no: str,
        amount: float,
        description: str
    ) -> Dict[str, Any]:
        if payment_method == "wechat":
            return await self.wechat.create_order(
                order_no=order_no,
                amount=int(amount * 100),
                description=description
            )
        elif payment_method == "alipay":
            return await self.alipay.create_order(
                order_no=order_no,
                amount=amount,
                subject=description
            )
        elif payment_method == "unionpay":
            return await self.unionpay.create_order(
                order_no=order_no,
                amount=int(amount * 100),
                subject=description
            )
        else:
            return {"success": False, "error": "不支持的支付方式"}
    
    async def query_payment(
        self,
        payment_method: str,
        order_no: str
    ) -> Dict[str, Any]:
        if payment_method == "wechat":
            return await self.wechat.query_order(order_no)
        elif payment_method == "alipay":
            return await self.alipay.query_order(order_no)
        elif payment_method == "unionpay":
            return await self.unionpay.query_order(order_no)
        else:
            return {"success": False, "error": "不支持的支付方式"}
    
    def verify_callback(
        self,
        payment_method: str,
        data: Any
    ) -> Dict[str, Any]:
        if payment_method == "wechat":
            return self.wechat.verify_callback(data)
        elif payment_method == "alipay":
            if isinstance(data, dict):
                return self.alipay.verify_callback(data)
            return {"success": False, "error": "数据格式错误"}
        elif payment_method == "unionpay":
            if isinstance(data, dict):
                return self.unionpay.verify_callback(data)
            return {"success": False, "error": "数据格式错误"}
        else:
            return {"success": False, "error": "不支持的支付方式"}


payment_service = PaymentService()
