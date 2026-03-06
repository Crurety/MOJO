"""用户行为分析和数据统计服务"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models import Message, Order, Task, User, UserPermission, Work


class AnalyticsService:
    """数据分析服务"""

    def __init__(self, db: Session):
        self.db = db

    # 用户数据分析
    def get_user_statistics(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Dict:
        """获取用户统计数据"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # 总用户数
        total_users = self.db.query(func.count(User.id)).scalar()

        # 新增用户
        new_users = (
            self.db.query(func.count(User.id))
            .filter(User.created_at.between(start_date, end_date))
            .scalar()
        )

        # 活跃用户（有登录记录）
        active_users = (
            self.db.query(func.count(User.id))
            .filter(User.last_login_at.between(start_date, end_date))
            .scalar()
        )

        # 付费用户
        paid_users = (
            self.db.query(func.count(func.distinct(Order.user_id)))
            .filter(Order.status == 1, Order.created_at.between(start_date, end_date))
            .scalar()
        )

        # 用户留存率（7天）
        seven_days_ago = datetime.now() - timedelta(days=7)
        new_users_7d = (
            self.db.query(User.id)
            .filter(
                User.created_at.between(
                    seven_days_ago - timedelta(days=1), seven_days_ago
                )
            )
            .all()
        )

        retained_users = 0
        if new_users_7d:
            user_ids = [u.id for u in new_users_7d]
            retained_users = (
                self.db.query(func.count(func.distinct(User.id)))
                .filter(User.id.in_(user_ids), User.last_login_at >= seven_days_ago)
                .scalar()
            )

        retention_rate = (
            (retained_users / len(new_users_7d) * 100) if new_users_7d else 0
        )

        return {
            "total_users": total_users,
            "new_users": new_users,
            "active_users": active_users,
            "paid_users": paid_users,
            "retention_rate_7d": round(retention_rate, 2),
            "conversion_rate": round(
                (paid_users / active_users * 100) if active_users else 0, 2
            ),
        }

    # 收入数据分析
    def get_revenue_statistics(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Dict:
        """获取收入统计数据"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # 总收入
        total_revenue = self.db.query(func.sum(Order.amount)).filter(
            Order.status == 1, Order.created_at.between(start_date, end_date)
        ).scalar() or Decimal(0)

        # 订单数
        total_orders = (
            self.db.query(func.count(Order.id))
            .filter(Order.status == 1, Order.created_at.between(start_date, end_date))
            .scalar()
        )

        # 平均客单价
        avg_order_value = (total_revenue / total_orders) if total_orders else Decimal(0)

        # 按支付方式统计
        payment_stats = (
            self.db.query(
                Order.payment_method,
                func.count(Order.id).label("count"),
                func.sum(Order.amount).label("amount"),
            )
            .filter(Order.status == 1, Order.created_at.between(start_date, end_date))
            .group_by(Order.payment_method)
            .all()
        )

        # 按订单类型统计
        order_type_stats = (
            self.db.query(
                Order.order_type,
                func.count(Order.id).label("count"),
                func.sum(Order.amount).label("amount"),
            )
            .filter(Order.status == 1, Order.created_at.between(start_date, end_date))
            .group_by(Order.order_type)
            .all()
        )

        return {
            "total_revenue": float(total_revenue),
            "total_orders": total_orders,
            "avg_order_value": float(avg_order_value),
            "payment_methods": [
                {
                    "method": p.payment_method,
                    "count": p.count,
                    "amount": float(p.amount),
                }
                for p in payment_stats
            ],
            "order_types": [
                {"type": o.order_type, "count": o.count, "amount": float(o.amount)}
                for o in order_type_stats
            ],
        }

    # 内容使用分析
    def get_content_statistics(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Dict:
        """获取内容使用统计"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # 任务统计
        task_stats = (
            self.db.query(
                Task.task_type,
                func.count(Task.id).label("count"),
                func.avg(Task.cost_amount).label("avg_cost"),
            )
            .filter(Task.created_at.between(start_date, end_date))
            .group_by(Task.task_type)
            .all()
        )

        # 任务状态分布
        status_stats = (
            self.db.query(Task.status, func.count(Task.id).label("count"))
            .filter(Task.created_at.between(start_date, end_date))
            .group_by(Task.status)
            .all()
        )

        # 作品统计
        work_stats = (
            self.db.query(Work.work_type, func.count(Work.id).label("count"))
            .filter(Work.created_at.between(start_date, end_date))
            .group_by(Work.work_type)
            .all()
        )

        return {
            "task_types": [
                {
                    "type": t.task_type,
                    "count": t.count,
                    "avg_cost": float(t.avg_cost or 0),
                }
                for t in task_stats
            ],
            "task_status": [
                {"status": s.status, "count": s.count} for s in status_stats
            ],
            "work_types": [{"type": w.work_type, "count": w.count} for w in work_stats],
        }

    # 用户行为漏斗分析
    def get_funnel_analysis(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Dict:
        """获取用户行为漏斗"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # 注册用户
        registered = (
            self.db.query(func.count(User.id))
            .filter(User.created_at.between(start_date, end_date))
            .scalar()
        )

        # 激活用户（有登录）
        activated = (
            self.db.query(func.count(User.id))
            .filter(
                User.created_at.between(start_date, end_date),
                User.last_login_at.isnot(None),
            )
            .scalar()
        )

        # 使用用户（创建过任务）
        used = (
            self.db.query(func.count(func.distinct(Task.user_id)))
            .join(User)
            .filter(User.created_at.between(start_date, end_date))
            .scalar()
        )

        # 付费用户
        paid = (
            self.db.query(func.count(func.distinct(Order.user_id)))
            .join(User)
            .filter(User.created_at.between(start_date, end_date), Order.status == 1)
            .scalar()
        )

        return {
            "registered": registered,
            "activated": activated,
            "used": used,
            "paid": paid,
            "activation_rate": round(
                (activated / registered * 100) if registered else 0, 2
            ),
            "usage_rate": round((used / activated * 100) if activated else 0, 2),
            "payment_rate": round((paid / used * 100) if used else 0, 2),
        }

    # 趋势分析
    def get_trend_data(self, metric: str, days: int = 30) -> List[Dict]:
        """获取趋势数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        if metric == "users":
            # 每日新增用户
            data = (
                self.db.query(
                    func.date(User.created_at).label("date"),
                    func.count(User.id).label("value"),
                )
                .filter(User.created_at.between(start_date, end_date))
                .group_by(func.date(User.created_at))
                .all()
            )

        elif metric == "revenue":
            # 每日收入
            data = (
                self.db.query(
                    func.date(Order.created_at).label("date"),
                    func.sum(Order.amount).label("value"),
                )
                .filter(
                    Order.status == 1, Order.created_at.between(start_date, end_date)
                )
                .group_by(func.date(Order.created_at))
                .all()
            )

        elif metric == "tasks":
            # 每日任务数
            data = (
                self.db.query(
                    func.date(Task.created_at).label("date"),
                    func.count(Task.id).label("value"),
                )
                .filter(Task.created_at.between(start_date, end_date))
                .group_by(func.date(Task.created_at))
                .all()
            )

        else:
            return []

        return [
            {"date": str(d.date), "value": float(d.value) if d.value else 0}
            for d in data
        ]

    # RFM分析
    def get_rfm_analysis(self) -> Dict:
        """RFM用户价值分析"""
        now = datetime.now()

        # 获取所有付费用户的RFM数据
        rfm_data = (
            self.db.query(
                Order.user_id,
                func.max(Order.created_at).label("last_order_date"),
                func.count(Order.id).label("frequency"),
                func.sum(Order.amount).label("monetary"),
            )
            .filter(Order.status == 1)
            .group_by(Order.user_id)
            .all()
        )

        # 计算RFM分数
        rfm_segments = {
            "high_value": 0,  # 高价值用户
            "potential": 0,  # 潜力用户
            "at_risk": 0,  # 流失风险用户
            "lost": 0,  # 已流失用户
        }

        for user in rfm_data:
            recency = (now - user.last_order_date).days
            frequency = user.frequency
            monetary = float(user.monetary)

            # 简单的RFM分段逻辑
            if recency <= 30 and frequency >= 3 and monetary >= 300:
                rfm_segments["high_value"] += 1
            elif recency <= 60 and frequency >= 2:
                rfm_segments["potential"] += 1
            elif recency <= 90:
                rfm_segments["at_risk"] += 1
            else:
                rfm_segments["lost"] += 1

        return rfm_segments
