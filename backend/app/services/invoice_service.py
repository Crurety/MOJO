"""发票服务"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.models.invoice import Invoice, UserRealName
from app.core.exceptions import BadRequestException
from decimal import Decimal


class InvoiceService:
    """发票服务"""

    def __init__(self, db: Session):
        self.db = db

    # 实名认证
    def submit_real_name(
        self,
        user_id: int,
        real_name: str,
        id_card: str,
        id_card_front: str = None,
        id_card_back: str = None
    ) -> UserRealName:
        """提交实名认证"""
        # 检查是否已提交
        existing = self.db.query(UserRealName).filter(
            UserRealName.user_id == user_id
        ).first()

        if existing:
            # 更新信息
            existing.real_name = real_name
            existing.id_card = id_card
            existing.id_card_front = id_card_front
            existing.id_card_back = id_card_back
            existing.status = 0  # 重新提交，状态改为待审核
            existing.reject_reason = None
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # 创建新记录
        real_name_info = UserRealName(
            user_id=user_id,
            real_name=real_name,
            id_card=id_card,
            id_card_front=id_card_front,
            id_card_back=id_card_back,
            status=0
        )

        self.db.add(real_name_info)
        self.db.commit()
        self.db.refresh(real_name_info)

        return real_name_info

    def get_real_name_status(self, user_id: int) -> Optional[UserRealName]:
        """获取实名认证状态"""
        return self.db.query(UserRealName).filter(
            UserRealName.user_id == user_id
        ).first()

    def verify_real_name(self, user_id: int, approved: bool, reject_reason: str = None) -> bool:
        """审核实名认证（管理员）"""
        real_name = self.db.query(UserRealName).filter(
            UserRealName.user_id == user_id
        ).first()

        if not real_name:
            return False

        if approved:
            real_name.status = 1
            real_name.verified_at = datetime.now()
            real_name.reject_reason = None
        else:
            real_name.status = 2
            real_name.reject_reason = reject_reason

        self.db.commit()
        return True

    # 发票管理
    def create_invoice(
        self,
        user_id: int,
        order_id: int,
        invoice_type: str,
        invoice_title: str,
        tax_no: str,
        amount: Decimal,
        recipient_name: str,
        recipient_phone: str,
        recipient_address: str,
        company_address: str = None,
        company_phone: str = None,
        bank_name: str = None,
        bank_account: str = None
    ) -> Invoice:
        """创建发票申请"""
        verified_real_name = (
            self.db.query(UserRealName)
            .filter(UserRealName.user_id == user_id, UserRealName.status == 1)
            .first()
        )
        if not verified_real_name:
            raise BadRequestException(detail="请先完成实名认证")

        invoice_no = self._generate_invoice_no()

        invoice = Invoice(
            user_id=user_id,
            order_id=order_id,
            invoice_no=invoice_no,
            invoice_type=invoice_type,
            invoice_title=invoice_title,
            tax_no=tax_no,
            amount=amount,
            company_address=company_address,
            company_phone=company_phone,
            bank_name=bank_name,
            bank_account=bank_account,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            recipient_address=recipient_address,
            status=0
        )

        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)

        return invoice

    def _generate_invoice_no(self) -> str:
        """生成发票编号"""
        from datetime import datetime
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = uuid.uuid4().hex[:6].upper()
        return f"INV{timestamp}{random_str}"

    def get_user_invoices(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Invoice]:
        """获取用户发票列表"""
        return self.db.query(Invoice).filter(
            Invoice.user_id == user_id
        ).order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    def get_invoice_by_no(self, invoice_no: str) -> Optional[Invoice]:
        """根据发票编号获取发票"""
        return self.db.query(Invoice).filter(Invoice.invoice_no == invoice_no).first()

    def update_invoice_status(
        self,
        invoice_id: int,
        status: int,
        invoice_url: str = None,
        tracking_no: str = None,
        reject_reason: str = None
    ) -> bool:
        """更新发票状态（管理员）"""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

        if not invoice:
            return False

        invoice.status = status

        if status == 1:  # 已开具
            invoice.issued_at = datetime.now()
            if invoice_url:
                invoice.invoice_url = invoice_url
        elif status == 2:  # 已邮寄
            invoice.mailed_at = datetime.now()
            if tracking_no:
                invoice.tracking_no = tracking_no
        elif status == 4:  # 已拒绝
            invoice.reject_reason = reject_reason

        self.db.commit()
        return True

    def get_pending_invoices(self, skip: int = 0, limit: int = 20) -> List[Invoice]:
        """获取待处理发票列表（管理员）"""
        return self.db.query(Invoice).filter(
            Invoice.status == 0
        ).order_by(Invoice.created_at).offset(skip).limit(limit).all()

    def get_all_invoices(
        self,
        status: int = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Invoice]:
        """获取所有发票列表（管理员）"""
        query = self.db.query(Invoice)

        if status is not None:
            query = query.filter(Invoice.status == status)

        return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()
