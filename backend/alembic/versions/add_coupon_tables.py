"""数据库迁移脚本 - 添加优惠券表"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = 'add_coupon_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建优惠券表
    op.create_table(
        'coupons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(50), nullable=False, comment='优惠券码'),
        sa.Column('name', sa.String(200), nullable=False, comment='优惠券名称'),
        sa.Column('coupon_type', sa.String(20), nullable=False, comment='类型: discount/amount/permission'),
        sa.Column('discount_value', sa.Numeric(10, 2), nullable=True, comment='折扣值或金额'),
        sa.Column('permission_type', sa.String(20), nullable=True, comment='权限类型'),
        sa.Column('permission_days', sa.Integer(), nullable=True, comment='权限天数'),
        sa.Column('min_amount', sa.Numeric(10, 2), nullable=False, default=0, comment='最低消费金额'),
        sa.Column('max_discount', sa.Numeric(10, 2), nullable=True, comment='最大优惠金额'),
        sa.Column('total_count', sa.Integer(), nullable=False, default=1, comment='总发放数量'),
        sa.Column('used_count', sa.Integer(), nullable=False, default=0, comment='已使用数量'),
        sa.Column('start_at', sa.DateTime(), nullable=False, comment='开始时间'),
        sa.Column('expire_at', sa.DateTime(), nullable=False, comment='过期时间'),
        sa.Column('status', sa.Integer(), nullable=False, default=1, comment='状态: 0禁用 1启用'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_coupons_code', 'coupons', ['code'], unique=True)

    # 创建用户优惠券表
    op.create_table(
        'user_coupons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('coupon_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=False, default=0, comment='状态: 0未使用 1已使用 2已过期'),
        sa.Column('used_at', sa.DateTime(), nullable=True, comment='使用时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'])
    )
    op.create_index('ix_user_coupons_user_id', 'user_coupons', ['user_id'])
    op.create_index('ix_user_coupons_coupon_id', 'user_coupons', ['coupon_id'])


def downgrade():
    op.drop_table('user_coupons')
    op.drop_table('coupons')
