"""自动化营销服务"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Order, User
from app.models.advanced_operation import AutomationExecution, AutomationRule
from app.services.coupon_service import CouponService
from app.services.member_service import MemberService
from app.services.push_service import PushService


class AutomationMarketingService:
    """自动化营销服务"""

    def __init__(self, db: Session):
        self.db = db
        self.push_service = PushService(db)
        try:
            self.coupon_service = CouponService(db)
        except:
            self.coupon_service = None
        self.member_service = MemberService(db)

    def create_rule(
        self,
        rule_name: str,
        rule_type: str,
        trigger_event: str,
        trigger_conditions: Dict,
        actions: List[Dict],
        status: int = 1,
    ) -> AutomationRule:
        """创建自动化规则

        Args:
            rule_name: 规则名称
            rule_type: 规则类型 (trigger/lifecycle/churn)
            trigger_event: 触发事件
            trigger_conditions: 触发条件
            actions: 执行动作列表
            status: 状态
        """
        rule = AutomationRule(
            rule_name=rule_name,
            rule_type=rule_type,
            trigger_event=trigger_event,
            trigger_conditions=json.dumps(trigger_conditions),
            actions=json.dumps(actions),
            status=status,
        )

        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)

        return rule

    def execute_rule(
        self, rule_id: int, user_id: int, trigger_data: Dict = None
    ) -> bool:
        """执行自动化规则

        Args:
            rule_id: 规则ID
            user_id: 用户ID
            trigger_data: 触发数据
        """
        rule = (
            self.db.query(AutomationRule)
            .filter(AutomationRule.id == rule_id, AutomationRule.status == 1)
            .first()
        )

        if not rule:
            return False

        # 检查触发条件
        if not self._check_conditions(
            user_id, json.loads(rule.trigger_conditions), trigger_data
        ):
            return False

        # 执行动作
        actions = json.loads(rule.actions)
        success = True

        for action in actions:
            try:
                self._execute_action(user_id, action)
            except Exception as e:
                success = False
                print(f"执行动作失败: {str(e)}")

        # 记录执行
        execution = AutomationExecution(
            rule_id=rule_id,
            user_id=user_id,
            trigger_data=json.dumps(trigger_data) if trigger_data else None,
            status=1 if success else 2,
            executed_at=datetime.now(),
        )

        self.db.add(execution)

        # 更新规则统计
        rule.execution_count += 1
        if success:
            rule.success_count += 1

        self.db.commit()

        return success

    def _check_conditions(
        self, user_id: int, conditions: Dict, trigger_data: Dict = None
    ) -> bool:
        """检查触发条件"""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        # 检查用户状态
        if "user_status" in conditions:
            if user.status != conditions["user_status"]:
                return False

        # 检查注册时间
        if "register_days" in conditions:
            days = (datetime.now() - user.created_at).days
            if (
                days < conditions["register_days"]["min"]
                or days > conditions["register_days"]["max"]
            ):
                return False

        # 检查最后登录时间
        if "last_login_days" in conditions and user.last_login_at:
            days = (datetime.now() - user.last_login_at).days
            if days < conditions["last_login_days"]:
                return False

        # 检查订单数
        if "order_count" in conditions:
            order_count = (
                self.db.query(Order)
                .filter(Order.user_id == user_id, Order.status == 1)
                .count()
            )

            if order_count < conditions["order_count"]["min"]:
                return False

        return True

    def _execute_action(self, user_id: int, action: Dict):
        """执行动作"""
        action_type = action.get("type")

        if action_type == "send_notification":
            # 发送通知
            self.push_service.send_to_user(
                user_id=user_id,
                notification_type="site",
                title=action.get("title"),
                content=action.get("content"),
                link=action.get("link"),
            )

        elif action_type == "send_coupon":
            # 发送优惠券
            if self.coupon_service:
                self.coupon_service.claim_coupon(user_id, action.get("coupon_code"))

        elif action_type == "add_points":
            # 增加积分
            self.member_service.add_points(
                user_id=user_id,
                points=action.get("points"),
                reason=action.get("reason", "自动化营销奖励"),
                related_type="automation",
                related_id=0,
            )

        elif action_type == "send_email":
            # 发送邮件（需要邮件服务）
            pass

        elif action_type == "send_sms":
            # 发送短信（需要短信服务）
            pass

    # 预设规则模板
    def create_welcome_rule(self):
        """创建欢迎新用户规则"""
        return self.create_rule(
            rule_name="欢迎新用户",
            rule_type="trigger",
            trigger_event="user_register",
            trigger_conditions={},
            actions=[
                {
                    "type": "send_notification",
                    "title": "欢迎加入AI创作平台！",
                    "content": "恭喜您成功注册，已为您准备了新人大礼包，快去查看吧！",
                    "link": "/new-user-rewards",
                },
                {"type": "add_points", "points": 100, "reason": "新用户注册奖励"},
            ],
        )

    def create_first_order_rule(self):
        """创建首单优惠规则"""
        return self.create_rule(
            rule_name="首单优惠提醒",
            rule_type="trigger",
            trigger_event="user_register",
            trigger_conditions={
                "register_days": {"min": 0, "max": 3},
                "order_count": {"min": 0},
            },
            actions=[
                {
                    "type": "send_notification",
                    "title": "🎁 首单7折优惠即将过期",
                    "content": "您的新人专享7折优惠券还有3天过期，快来体验AI创作的魅力吧！",
                    "link": "/pricing",
                }
            ],
        )

    def create_churn_prevention_rule(self):
        """创建流失预防规则"""
        return self.create_rule(
            rule_name="流失用户召回",
            rule_type="churn",
            trigger_event="user_inactive",
            trigger_conditions={"last_login_days": 7},
            actions=[
                {
                    "type": "send_notification",
                    "title": "好久不见，我们为您准备了专属福利",
                    "content": "7天未见，甚是想念！特别为您准备了回归专享优惠券，快来看看吧~",
                    "link": "/comeback-offer",
                },
                {"type": "send_coupon", "coupon_code": "COMEBACK2024"},
            ],
        )

    def create_lifecycle_rule(self):
        """创建生命周期营销规则"""
        return self.create_rule(
            rule_name="注册7天未付费提醒",
            rule_type="lifecycle",
            trigger_event="user_lifecycle",
            trigger_conditions={
                "register_days": {"min": 7, "max": 7},
                "order_count": {"min": 0},
            },
            actions=[
                {
                    "type": "send_notification",
                    "title": "专属优惠等您来领",
                    "content": "感谢您注册7天！为您准备了专属优惠，立即使用可享受8折优惠！",
                    "link": "/special-offer",
                }
            ],
        )

    def get_active_rules(self, rule_type: str = None) -> List[AutomationRule]:
        """获取活跃规则"""
        query = self.db.query(AutomationRule).filter(AutomationRule.status == 1)

        if rule_type:
            query = query.filter(AutomationRule.rule_type == rule_type)

        return query.all()

    def get_rule_statistics(self, rule_id: int) -> Dict:
        """获取规则统计"""
        rule = (
            self.db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
        )

        if not rule:
            return {}

        return {
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "execution_count": rule.execution_count,
            "success_count": rule.success_count,
            "success_rate": round(
                (rule.success_count / rule.execution_count * 100)
                if rule.execution_count
                else 0,
                2,
            ),
            "status": rule.status,
            "created_at": rule.created_at,
        }

    def trigger_lifecycle_marketing(self):
        """触发生命周期营销（定时任务）"""
        # 获取所有生命周期规则
        rules = self.get_active_rules("lifecycle")

        count = 0
        for rule in rules:
            conditions = json.loads(rule.trigger_conditions)

            # 查找符合条件的用户
            if "register_days" in conditions:
                target_date = datetime.now() - timedelta(
                    days=conditions["register_days"]["min"]
                )

                users = (
                    self.db.query(User)
                    .filter(
                        User.created_at
                        >= target_date.replace(hour=0, minute=0, second=0),
                        User.created_at
                        < target_date.replace(hour=23, minute=59, second=59),
                    )
                    .all()
                )

                for user in users:
                    self.execute_rule(rule.id, user.id)
                    count += 1

        return count
