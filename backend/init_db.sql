-- AI创作平台数据库初始化脚本
-- 数据库: ai_platform
-- 字符集: utf8mb4

CREATE DATABASE IF NOT EXISTS ai_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_platform;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) UNIQUE COMMENT '手机号',
    password VARCHAR(255) NOT NULL COMMENT '密码(加密)',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(500) COMMENT '头像URL',
    status TINYINT DEFAULT 1 NOT NULL COMMENT '状态: 0禁用 1正常',
    balance DECIMAL(10,2) DEFAULT 0.00 NOT NULL COMMENT '账户余额',
    invite_code VARCHAR(20) UNIQUE COMMENT '邀请码',
    invited_by BIGINT COMMENT '邀请人ID',
    last_login_at DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) COMMENT '最后登录IP',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_invite_code (invite_code),
    INDEX idx_invited_by (invited_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 用户权限表
CREATE TABLE IF NOT EXISTS user_permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    permission_type VARCHAR(20) NOT NULL COMMENT '权限类型: script/image/video/ad',
    payment_mode VARCHAR(20) NOT NULL COMMENT '付费模式: per_use/monthly/yearly',
    total_count INT DEFAULT 0 NOT NULL COMMENT '总次数(按次付费)',
    used_count INT DEFAULT 0 NOT NULL COMMENT '已使用次数',
    expire_at DATETIME COMMENT '到期时间(包月/包年)',
    status TINYINT DEFAULT 1 NOT NULL COMMENT '状态: 0无效 1有效',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_permission_type (permission_type),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户权限表';

-- 脚本表
CREATE TABLE IF NOT EXISTS scripts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    title VARCHAR(200) COMMENT '标题',
    content TEXT NOT NULL COMMENT '脚本内容',
    output_type VARCHAR(20) NOT NULL COMMENT '输出类型: image_set/single_image/video',
    parameters JSON COMMENT '生成参数JSON',
    status TINYINT DEFAULT 1 NOT NULL COMMENT '状态: 0草稿 1已生成',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='脚本表';

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    task_no VARCHAR(50) UNIQUE NOT NULL COMMENT '任务编号',
    task_type VARCHAR(20) NOT NULL COMMENT '任务类型: script/image/video/ad',
    status TINYINT DEFAULT 0 NOT NULL COMMENT '状态: 0排队 1处理中 2完成 3失败',
    progress INT DEFAULT 0 NOT NULL COMMENT '进度百分比',
    parameters JSON COMMENT '任务参数JSON',
    result_url VARCHAR(500) COMMENT '结果URL',
    error_message TEXT COMMENT '错误信息',
    cost_amount INT DEFAULT 0 NOT NULL COMMENT '消耗使用量',
    completed_at DATETIME COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_task_no (task_no),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务表';

-- 作品表
CREATE TABLE IF NOT EXISTS works (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    task_id BIGINT COMMENT '任务ID',
    work_type VARCHAR(20) NOT NULL COMMENT '作品类型: image/video/ad',
    title VARCHAR(200) COMMENT '标题',
    file_url VARCHAR(500) NOT NULL COMMENT '文件URL',
    thumbnail_url VARCHAR(500) COMMENT '缩略图URL',
    parameters JSON COMMENT '生成参数JSON',
    is_public TINYINT DEFAULT 0 NOT NULL COMMENT '是否公开: 0否 1是',
    quality_score INT COMMENT '质量评分(用于作品集筛选)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_task_id (task_id),
    INDEX idx_work_type (work_type),
    INDEX idx_is_public (is_public),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品表';

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    order_no VARCHAR(50) UNIQUE NOT NULL COMMENT '订单编号',
    order_type VARCHAR(20) NOT NULL COMMENT '订单类型: permission/balance',
    product_name VARCHAR(200) NOT NULL COMMENT '商品名称',
    amount DECIMAL(10,2) NOT NULL COMMENT '订单金额',
    payment_method VARCHAR(20) COMMENT '支付方式: wechat/alipay/unionpay/balance',
    payment_no VARCHAR(100) COMMENT '第三方支付单号',
    status TINYINT DEFAULT 0 NOT NULL COMMENT '状态: 0待支付 1已支付 2已取消 3已退款',
    paid_at DATETIME COMMENT '支付时间',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_order_no (order_no),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    title VARCHAR(200) NOT NULL COMMENT '消息标题',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type VARCHAR(20) NOT NULL COMMENT '消息类型: system/task/promotion',
    is_read TINYINT DEFAULT 0 NOT NULL COMMENT '是否已读: 0否 1是',
    link VARCHAR(500) COMMENT '相关链接',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_message_type (message_type),
    INDEX idx_is_read (is_read),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- 管理员表
CREATE TABLE IF NOT EXISTS admins (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码(加密)',
    nickname VARCHAR(50) COMMENT '昵称',
    email VARCHAR(100) COMMENT '邮箱',
    role VARCHAR(20) DEFAULT 'admin' NOT NULL COMMENT '角色: super_admin/admin',
    status TINYINT DEFAULT 1 NOT NULL COMMENT '状态: 0禁用 1正常',
    last_login_at DATETIME COMMENT '最后登录时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    config_value TEXT NOT NULL COMMENT '配置值',
    description VARCHAR(500) COMMENT '配置说明',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- 优惠券表
CREATE TABLE IF NOT EXISTS coupons (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL COMMENT '优惠券码',
    coupon_type VARCHAR(20) NOT NULL COMMENT '类型: discount/cash/trial',
    value DECIMAL(10,2) NOT NULL COMMENT '优惠值(折扣/金额)',
    min_amount DECIMAL(10,2) DEFAULT 0 COMMENT '最低消费金额',
    max_use_count INT DEFAULT 1 COMMENT '最大使用次数',
    used_count INT DEFAULT 0 COMMENT '已使用次数',
    start_at DATETIME NOT NULL COMMENT '开始时间',
    end_at DATETIME NOT NULL COMMENT '结束时间',
    status TINYINT DEFAULT 1 NOT NULL COMMENT '状态: 0禁用 1有效',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_code (code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='优惠券表';

-- 用户优惠券关联表
CREATE TABLE IF NOT EXISTS user_coupons (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    coupon_id BIGINT NOT NULL COMMENT '优惠券ID',
    order_id BIGINT COMMENT '使用的订单ID',
    status TINYINT DEFAULT 0 NOT NULL COMMENT '状态: 0未使用 1已使用 2已过期',
    used_at DATETIME COMMENT '使用时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_coupon_id (coupon_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户优惠券关联表';

-- 操作日志表(存储到MongoDB，此处仅作记录)
-- CREATE TABLE IF NOT EXISTS operation_logs (
--     id BIGINT PRIMARY KEY AUTO_INCREMENT,
--     user_id BIGINT COMMENT '用户ID',
--     action VARCHAR(100) NOT NULL COMMENT '操作类型',
--     target_type VARCHAR(50) COMMENT '目标类型',
--     target_id BIGINT COMMENT '目标ID',
--     details JSON COMMENT '操作详情',
--     ip VARCHAR(50) COMMENT 'IP地址',
--     user_agent VARCHAR(500) COMMENT '用户代理',
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
--     INDEX idx_user_id (user_id),
--     INDEX idx_action (action),
--     INDEX idx_created_at (created_at)
-- ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- 插入默认系统配置
INSERT INTO system_configs (config_key, config_value, description) VALUES
('script_price_per_use', '1', '文字生成脚本按次价格'),
('script_price_monthly', '29', '文字生成脚本包月价格'),
('script_price_yearly', '199', '文字生成脚本包年价格'),
('image_price_per_use', '3', '图片生成按次价格'),
('image_price_monthly', '99', '图片生成包月价格'),
('image_price_yearly', '699', '图片生成包年价格'),
('video_price_per_use', '5', '视频生成按次价格'),
('video_price_monthly', '199', '视频生成包月价格'),
('video_price_yearly', '1399', '视频生成包年价格'),
('ad_price_per_use', '8', '广告设计按次价格'),
('ad_price_monthly', '299', '广告设计包月价格'),
('ad_price_yearly', '1999', '广告设计包年价格'),
('weight_720p', '1.0', '720P清晰度权重'),
('weight_1080p', '1.5', '1080P清晰度权重'),
('weight_4k', '2.5', '4K清晰度权重'),
('work_retention_days', '15', '作品保留天数'),
('task_retention_days', '30', '任务保留天数');

-- 插入默认管理员账号(密码: admin123)
INSERT INTO admins (username, password, nickname, email, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.qVh.N8.N8.N8.N', '超级管理员', 'admin@example.com', 'super_admin');
