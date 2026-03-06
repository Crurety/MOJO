import re
from typing import Optional


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    if len(password) < 6:
        return False, "密码长度至少6位"
    if len(password) > 50:
        return False, "密码长度不能超过50位"
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含字母"
    return True, None


def sanitize_string(text: str, max_length: int = 500) -> str:
    text = text.strip()
    text = re.sub(r'javascript\s*:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    if len(text) > max_length:
        text = text[:max_length]
    return text


def generate_order_no(prefix: str = "O") -> str:
    from datetime import datetime
    import uuid
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = uuid.uuid4().hex[:6].upper()
    return f"{prefix}{timestamp}{random_str}"


def generate_task_no() -> str:
    return generate_order_no("T")


def calculate_cost(
    task_type: str,
    clarity: str = "1080p",
    duration: int = 0,
    count: int = 1,
    width: int = 1920,
    height: int = 1080
) -> int:
    """计算任务消耗的使用量

    Args:
        task_type: 任务类型 (script/image/video/ad)
        clarity: 清晰度 (720p/1080p/4k)
        duration: 视频时长（秒）
        count: 生成数量
        width: 图片宽度
        height: 图片高度

    Returns:
        int: 消耗的使用量
    """
    # 清晰度权重系数
    clarity_weights = {
        "720p": 1.0,
        "1080p": 1.5,
        "2k": 2.0,
        "4k": 2.5,
        "8k": 4.0
    }

    # 基础消耗
    base_costs = {
        "script": 1,
        "image": 3,
        "video": 5,
        "ad": 8
    }

    # 尺寸权重系数（基于像素总数）
    def get_size_weight(w: int, h: int) -> float:
        pixels = w * h
        if pixels <= 1280 * 720:  # 720p
            return 1.0
        elif pixels <= 1920 * 1080:  # 1080p
            return 1.5
        elif pixels <= 2560 * 1440:  # 2K
            return 2.0
        elif pixels <= 3840 * 2160:  # 4K
            return 2.5
        else:  # 8K+
            return 4.0

    base_cost = base_costs.get(task_type, 1)
    clarity_weight = clarity_weights.get(clarity, 1.0)

    if task_type == "video":
        # 视频：基础消耗 × 清晰度系数 × 时长系数
        # 每30秒为一个基础单位
        duration_weight = max(1.0, duration / 30.0)
        cost = base_cost * clarity_weight * duration_weight
    elif task_type == "image":
        # 图片：基础消耗 × 清晰度系数 × 尺寸系数 × 数量
        size_weight = get_size_weight(width, height)
        cost = base_cost * clarity_weight * size_weight * count
    elif task_type == "ad":
        # 广告：基础消耗 × 复杂度系数（根据素材数量）
        complexity_weight = max(1.0, count / 3.0)  # 每3个素材增加复杂度
        cost = base_cost * complexity_weight
    else:
        # 脚本：基础消耗 × 数量
        cost = base_cost * count

    return max(1, int(cost))
