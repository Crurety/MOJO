"""工具函数单元测试"""
import pytest
from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_password,
    sanitize_string,
    generate_order_no,
    generate_task_no,
    calculate_cost,
)


# ============= 邮箱验证 =============

class TestValidateEmail:

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "test.user@example.com",
        "test+tag@example.co.uk",
        "123@example.com",
    ])
    def test_valid_emails(self, email):
        assert validate_email(email) is True

    @pytest.mark.parametrize("email", [
        "",
        "notanemail",
        "@example.com",
        "user@",
        "user@.com",
        "user@com",
    ])
    def test_invalid_emails(self, email):
        assert validate_email(email) is False


# ============= 手机号验证 =============

class TestValidatePhone:

    @pytest.mark.parametrize("phone", [
        "13800138000",
        "15912345678",
        "18612345678",
        "17700001111",
    ])
    def test_valid_phones(self, phone):
        assert validate_phone(phone) is True

    @pytest.mark.parametrize("phone", [
        "",
        "12345",
        "12345678901",  # 以1开头但第二位是2
        "23800138000",  # 不以1开头
        "1380013800",   # 10位
        "138001380001",  # 12位
        "abcdefghijk",
    ])
    def test_invalid_phones(self, phone):
        assert validate_phone(phone) is False


# ============= 密码验证 =============

class TestValidatePassword:

    def test_valid_password(self):
        valid, msg = validate_password("Test123456")
        assert valid is True
        assert msg is None

    def test_too_short(self):
        valid, msg = validate_password("Ab1")
        assert valid is False
        assert "6" in msg

    def test_too_long(self):
        valid, msg = validate_password("a" * 51)
        assert valid is False
        assert "50" in msg

    def test_no_letter(self):
        valid, msg = validate_password("123456789")
        assert valid is False
        assert "字母" in msg

    def test_minimum_valid(self):
        valid, msg = validate_password("abcdef")
        assert valid is True


# ============= 字符串过滤 =============

class TestSanitizeString:

    def test_strip_whitespace(self):
        assert sanitize_string("  hello  ") == "hello"

    def test_remove_html_tags(self):
        assert sanitize_string("<script>alert('xss')</script>hello") == "alert('xss')hello"
        assert sanitize_string("<b>bold</b>") == "bold"

    def test_truncate_long_string(self):
        long_str = "a" * 1000
        result = sanitize_string(long_str, max_length=100)
        assert len(result) == 100

    def test_normal_string(self):
        assert sanitize_string("正常文本") == "正常文本"


# ============= 编号生成 =============

class TestGenerateOrderNo:

    def test_format(self):
        no = generate_order_no()
        assert no.startswith("O")
        assert len(no) == 21  # O + 14位时间戳 + 6位随机

    def test_custom_prefix(self):
        no = generate_order_no("INV")
        assert no.startswith("INV")

    def test_uniqueness(self):
        nos = {generate_order_no() for _ in range(100)}
        assert len(nos) == 100  # 100个全部唯一

    def test_task_no(self):
        no = generate_task_no()
        assert no.startswith("T")


# ============= 费用计算 =============

class TestCalculateCost:

    # 脚本
    def test_script_base(self):
        assert calculate_cost("script") == 1

    def test_script_multiple(self):
        assert calculate_cost("script", count=5) == 5

    # 图片
    def test_image_720p(self):
        cost = calculate_cost("image", clarity="720p", width=1280, height=720)
        assert cost == 3  # 3 * 1.0 * 1.0

    def test_image_1080p(self):
        cost = calculate_cost("image", clarity="1080p", width=1920, height=1080)
        assert cost == 6  # 3 * 1.5 * 1.5 = 6.75 → 6

    def test_image_4k(self):
        cost = calculate_cost("image", clarity="4k", width=3840, height=2160)
        assert cost >= 15  # 3 * 2.5 * 2.5

    def test_image_multiple(self):
        cost = calculate_cost("image", clarity="720p", count=3, width=1280, height=720)
        assert cost == 9  # 3 * 1.0 * 1.0 * 3

    # 视频
    def test_video_short(self):
        cost = calculate_cost("video", clarity="1080p", duration=10)
        assert cost == 7  # 5 * 1.5 * 1.0

    def test_video_60s(self):
        cost = calculate_cost("video", clarity="1080p", duration=60)
        assert cost == 15  # 5 * 1.5 * 2.0

    def test_video_4k_long(self):
        cost = calculate_cost("video", clarity="4k", duration=120)
        assert cost >= 40  # 5 * 2.5 * (120/30)

    # 广告
    def test_ad_base(self):
        assert calculate_cost("ad") == 8

    def test_ad_complex(self):
        cost = calculate_cost("ad", count=9)
        assert cost == 24  # 8 * (9/3)

    # 边界
    def test_minimum_cost(self):
        assert calculate_cost("script") >= 1

    def test_unknown_type(self):
        cost = calculate_cost("unknown")
        assert cost >= 1

    def test_unknown_clarity(self):
        cost = calculate_cost("image", clarity="unknown")
        assert cost >= 1
