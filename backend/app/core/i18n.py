"""错误消息国际化模块"""
from typing import Dict, Any


class I18n:
    """国际化支持类"""
    
    # 支持的语言
    SUPPORTED_LANGUAGES = ["zh", "en"]
    
    # 默认语言
    DEFAULT_LANGUAGE = "zh"
    
    # 错误消息字典
    MESSAGES: Dict[str, Dict[str, str]] = {
        "zh": {
            # 通用错误
            "success": "操作成功",
            "error": "操作失败",
            "invalid_params": "参数错误",
            "not_found": "资源不存在",
            "unauthorized": "未授权访问",
            "forbidden": "权限不足",
            "internal_error": "服务器内部错误",
            
            # 用户相关
            "user_not_found": "用户不存在",
            "user_disabled": "用户已被禁用",
            "email_exists": "邮箱已被注册",
            "phone_exists": "手机号已被注册",
            "invalid_email": "邮箱格式不正确",
            "invalid_phone": "手机号格式不正确",
            "invalid_password": "密码格式不正确",
            "password_mismatch": "密码不匹配",
            "login_failed": "登录失败，请检查账号密码",
            
            # 认证相关
            "token_expired": "Token已过期",
            "token_invalid": "Token无效",
            "token_missing": "Token缺失",
            
            # 权限相关
            "permission_denied": "权限不足",
            "permission_not_found": "权限不存在",
            "permission_expired": "权限已过期",
            "permission_insufficient": "权限次数不足",
            
            # 订单相关
            "order_not_found": "订单不存在",
            "order_paid": "订单已支付",
            "order_cancelled": "订单已取消",
            "order_expired": "订单已过期",
            "payment_failed": "支付失败",
            
            # 内容相关
            "script_not_found": "脚本不存在",
            "task_not_found": "任务不存在",
            "work_not_found": "作品不存在",
            "task_failed": "任务执行失败",
            
            # 优惠券相关
            "coupon_not_found": "优惠券不存在",
            "coupon_expired": "优惠券已过期",
            "coupon_used": "优惠券已使用",
            "coupon_unavailable": "优惠券不可用",
            
            # 工单相关
            "ticket_not_found": "工单不存在",
            "ticket_closed": "工单已关闭",
            
            # 发票相关
            "invoice_not_found": "发票不存在",
            "real_name_not_verified": "实名认证未通过",
            
            # 速率限制
            "rate_limit_exceeded": "请求过于频繁，请稍后再试",
        },
        "en": {
            # Common errors
            "success": "Success",
            "error": "Operation failed",
            "invalid_params": "Invalid parameters",
            "not_found": "Resource not found",
            "unauthorized": "Unauthorized access",
            "forbidden": "Permission denied",
            "internal_error": "Internal server error",
            
            # User related
            "user_not_found": "User not found",
            "user_disabled": "User is disabled",
            "email_exists": "Email already registered",
            "phone_exists": "Phone number already registered",
            "invalid_email": "Invalid email format",
            "invalid_phone": "Invalid phone number format",
            "invalid_password": "Invalid password format",
            "password_mismatch": "Password mismatch",
            "login_failed": "Login failed, please check your credentials",
            
            # Authentication related
            "token_expired": "Token has expired",
            "token_invalid": "Invalid token",
            "token_missing": "Token is missing",
            
            # Permission related
            "permission_denied": "Permission denied",
            "permission_not_found": "Permission not found",
            "permission_expired": "Permission has expired",
            "permission_insufficient": "Insufficient permission count",
            
            # Order related
            "order_not_found": "Order not found",
            "order_paid": "Order already paid",
            "order_cancelled": "Order has been cancelled",
            "order_expired": "Order has expired",
            "payment_failed": "Payment failed",
            
            # Content related
            "script_not_found": "Script not found",
            "task_not_found": "Task not found",
            "work_not_found": "Work not found",
            "task_failed": "Task execution failed",
            
            # Coupon related
            "coupon_not_found": "Coupon not found",
            "coupon_expired": "Coupon has expired",
            "coupon_used": "Coupon already used",
            "coupon_unavailable": "Coupon unavailable",
            
            # Ticket related
            "ticket_not_found": "Ticket not found",
            "ticket_closed": "Ticket is closed",
            
            # Invoice related
            "invoice_not_found": "Invoice not found",
            "real_name_not_verified": "Real name verification not passed",
            
            # Rate limit
            "rate_limit_exceeded": "Too many requests, please try again later",
        }
    }
    
    @classmethod
    def get_message(cls, key: str, language: str = None, **kwargs) -> str:
        """获取国际化消息
        
        Args:
            key: 消息键
            language: 语言代码 (zh/en)
            **kwargs: 格式化参数
        
        Returns:
            str: 国际化消息
        """
        if language is None:
            language = cls.DEFAULT_LANGUAGE
        
        if language not in cls.SUPPORTED_LANGUAGES:
            language = cls.DEFAULT_LANGUAGE
        
        messages = cls.MESSAGES.get(language, cls.MESSAGES[cls.DEFAULT_LANGUAGE])
        message = messages.get(key, cls.MESSAGES[cls.DEFAULT_LANGUAGE].get(key, key))
        
        # 格式化消息
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return message
    
    @classmethod
    def set_language(cls, language: str):
        """设置默认语言
        
        Args:
            language: 语言代码
        """
        if language in cls.SUPPORTED_LANGUAGES:
            cls.DEFAULT_LANGUAGE = language


def get_error_message(key: str, language: str = None, **kwargs) -> str:
    """获取错误消息的便捷函数
    
    Args:
        key: 消息键
        language: 语言代码
        **kwargs: 格式化参数
    
    Returns:
        str: 国际化消息
    """
    return I18n.get_message(key, language, **kwargs)
