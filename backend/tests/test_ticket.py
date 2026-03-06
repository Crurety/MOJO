"""工单系统测试"""

import pytest


def test_create_ticket(client, auth_headers):
    """测试创建工单"""
    response = client.post(
        "/api/v1/ticket/tickets",
        json={
            "category": "技术问题",
            "subject": "测试工单",
            "content": "这是一个测试工单",
            "priority": 2,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "ticket_no" in data["data"]


def test_get_my_tickets(client, auth_headers):
    """测试获取我的工单"""
    response = client.get("/api/v1/ticket/tickets", headers=auth_headers)
    assert response.status_code == 200


def test_create_feedback(client, auth_headers):
    """测试提交反馈"""
    response = client.post(
        "/api/v1/ticket/feedbacks",
        json={
            "feedback_type": "功能建议",
            "content": "希望增加XX功能",
            "contact": "test@example.com",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_get_my_feedbacks(client, auth_headers):
    """测试获取我的反馈"""
    response = client.get("/api/v1/ticket/feedbacks", headers=auth_headers)
    assert response.status_code == 200
