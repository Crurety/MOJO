"""数据库索引优化迁移"""

from alembic import op
import sqlalchemy as sa

revision = 'add_performance_indexes'
down_revision = 'add_coupon_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 消息表索引优化
    op.create_index('ix_messages_user_id_is_read', 'messages', ['user_id', 'is_read'])
    op.create_index('ix_messages_user_id_created_at', 'messages', ['user_id', 'created_at'])
    op.create_index('ix_messages_message_type', 'messages', ['message_type'])

    # 任务表索引优化
    op.create_index('ix_tasks_user_id_status', 'tasks', ['user_id', 'status'])
    op.create_index('ix_tasks_status_created_at', 'tasks', ['status', 'created_at'])
    op.create_index('ix_tasks_task_type', 'tasks', ['task_type'])

    # 作品表索引优化
    op.create_index('ix_works_user_id_work_type', 'works', ['user_id', 'work_type'])
    op.create_index('ix_works_is_public_quality_score', 'works', ['is_public', 'quality_score'])
    op.create_index('ix_works_created_at', 'works', ['created_at'])

    # 订单表索引优化
    op.create_index('ix_orders_user_id_status', 'orders', ['user_id', 'status'])
    op.create_index('ix_orders_status_created_at', 'orders', ['status', 'created_at'])
    op.create_index('ix_orders_payment_method', 'orders', ['payment_method'])

    # 权限表索引优化
    op.create_index('ix_user_permissions_user_id_status', 'user_permissions', ['user_id', 'status'])
    op.create_index('ix_user_permissions_expire_at', 'user_permissions', ['expire_at'])

    # 优惠券表索引优化
    op.create_index('ix_coupons_status_expire_at', 'coupons', ['status', 'expire_at'])
    op.create_index('ix_user_coupons_user_id_status', 'user_coupons', ['user_id', 'status'])


def downgrade():
    # 删除索引
    op.drop_index('ix_messages_user_id_is_read', 'messages')
    op.drop_index('ix_messages_user_id_created_at', 'messages')
    op.drop_index('ix_messages_message_type', 'messages')

    op.drop_index('ix_tasks_user_id_status', 'tasks')
    op.drop_index('ix_tasks_status_created_at', 'tasks')
    op.drop_index('ix_tasks_task_type', 'tasks')

    op.drop_index('ix_works_user_id_work_type', 'works')
    op.drop_index('ix_works_is_public_quality_score', 'works')
    op.drop_index('ix_works_created_at', 'works')

    op.drop_index('ix_orders_user_id_status', 'orders')
    op.drop_index('ix_orders_status_created_at', 'orders')
    op.drop_index('ix_orders_payment_method', 'orders')

    op.drop_index('ix_user_permissions_user_id_status', 'user_permissions')
    op.drop_index('ix_user_permissions_expire_at', 'user_permissions')

    op.drop_index('ix_coupons_status_expire_at', 'coupons')
    op.drop_index('ix_user_coupons_user_id_status', 'user_coupons')
