"""AB测试服务"""

import hashlib
import random
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.advanced_operation import (
    ABTest,
    ABTestMetric,
    ABTestUserAssignment,
    ABTestVariant,
)


class ABTestService:
    """AB测试服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_test(
        self,
        test_name: str,
        test_type: str,
        description: str,
        variants: List[Dict],
        start_at: datetime,
        end_at: datetime,
        target_users: str = "all",
    ) -> ABTest:
        """创建AB测试

        Args:
            test_name: 测试名称
            test_type: 测试类型 (ui/feature/price/content)
            description: 测试描述
            variants: 变体列表 [{"name": "A", "config": {...}, "traffic": 50}]
            start_at: 开始时间
            end_at: 结束时间
            target_users: 目标用户 (all/new/paid)
        """
        test = ABTest(
            test_name=test_name,
            test_type=test_type,
            description=description,
            start_at=start_at,
            end_at=end_at,
            target_users=target_users,
            status=1,
        )

        self.db.add(test)
        self.db.flush()

        # 创建变体
        for variant_data in variants:
            variant = ABTestVariant(
                test_id=test.id,
                variant_name=variant_data["name"],
                variant_config=str(variant_data.get("config", {})),
                traffic_percentage=variant_data.get("traffic", 50),
            )
            self.db.add(variant)

        self.db.commit()
        self.db.refresh(test)

        return test

    def assign_user_to_variant(self, test_id: int, user_id: int) -> Optional[str]:
        """分配用户到变体

        使用一致性哈希确保同一用户始终分配到同一变体
        """
        # 检查是否已分配
        existing = (
            self.db.query(ABTestUserAssignment)
            .filter(
                ABTestUserAssignment.test_id == test_id,
                ABTestUserAssignment.user_id == user_id,
            )
            .first()
        )

        if existing:
            return existing.variant_name

        # 获取测试和变体
        test = self.db.query(ABTest).filter(ABTest.id == test_id).first()
        if not test or test.status != 1:
            return None

        variants = (
            self.db.query(ABTestVariant).filter(ABTestVariant.test_id == test_id).all()
        )

        if not variants:
            return None

        # 使用一致性哈希分配
        hash_input = f"{test_id}_{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        percentage = hash_value % 100

        # 根据流量百分比分配
        cumulative = 0
        selected_variant = None

        for variant in variants:
            cumulative += variant.traffic_percentage
            if percentage < cumulative:
                selected_variant = variant.variant_name
                break

        if not selected_variant:
            selected_variant = variants[0].variant_name

        # 记录分配
        assignment = ABTestUserAssignment(
            test_id=test_id, user_id=user_id, variant_name=selected_variant
        )

        self.db.add(assignment)
        self.db.commit()

        return selected_variant

    def record_metric(
        self, test_id: int, user_id: int, metric_name: str, metric_value: str
    ):
        """记录测试指标"""
        # 获取用户分配的变体
        assignment = (
            self.db.query(ABTestUserAssignment)
            .filter(
                ABTestUserAssignment.test_id == test_id,
                ABTestUserAssignment.user_id == user_id,
            )
            .first()
        )

        if not assignment:
            return

        metric = ABTestMetric(
            test_id=test_id,
            user_id=user_id,
            variant=assignment.variant_name,
            metric_name=metric_name,
            metric_value=metric_value,
        )

        self.db.add(metric)
        self.db.commit()

    def get_test_results(self, test_id: int) -> Dict:
        """获取测试结果"""
        from sqlalchemy import func

        test = self.db.query(ABTest).filter(ABTest.id == test_id).first()
        if not test:
            return {}

        # 获取各变体的用户数
        variant_users = (
            self.db.query(
                ABTestUserAssignment.variant_name,
                func.count(ABTestUserAssignment.user_id).label("user_count"),
            )
            .filter(ABTestUserAssignment.test_id == test_id)
            .group_by(ABTestUserAssignment.variant_name)
            .all()
        )

        # 获取各变体的指标数据
        variant_metrics = (
            self.db.query(
                ABTestMetric.variant,
                ABTestMetric.metric_name,
                func.count(ABTestMetric.id).label("count"),
                func.avg(func.cast(ABTestMetric.metric_value, Integer)).label(
                    "avg_value"
                ),
            )
            .filter(ABTestMetric.test_id == test_id)
            .group_by(ABTestMetric.variant, ABTestMetric.metric_name)
            .all()
        )

        # 组织结果
        results = {
            "test_name": test.test_name,
            "test_type": test.test_type,
            "status": test.status,
            "variants": {},
        }

        # 用户数统计
        for variant, count in variant_users:
            if variant not in results["variants"]:
                results["variants"][variant] = {"user_count": count, "metrics": {}}

        # 指标统计
        for variant, metric_name, count, avg_value in variant_metrics:
            if variant in results["variants"]:
                results["variants"][variant]["metrics"][metric_name] = {
                    "count": count,
                    "avg_value": float(avg_value) if avg_value else 0,
                }

        return results

    def end_test(self, test_id: int, winner_variant: str = None):
        """结束测试"""
        test = self.db.query(ABTest).filter(ABTest.id == test_id).first()

        if test:
            test.status = 2
            test.winner_variant = winner_variant
            self.db.commit()

    def get_active_tests(self) -> List[ABTest]:
        """获取进行中的测试"""
        now = datetime.now()
        return (
            self.db.query(ABTest)
            .filter(ABTest.status == 1, ABTest.start_at <= now, ABTest.end_at >= now)
            .all()
        )


from sqlalchemy import Integer
