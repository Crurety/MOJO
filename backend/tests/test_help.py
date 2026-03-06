"""帮助中心功能测试"""

import pytest


def test_get_categories(client):
    """测试获取帮助分类"""
    response = client.get("/api/v1/help/categories")
    assert response.status_code == 200


def test_get_articles(client):
    """测试获取文章列表"""
    response = client.get("/api/v1/help/articles")
    assert response.status_code == 200


def test_get_faqs(client):
    """测试获取FAQ列表"""
    response = client.get("/api/v1/help/faqs")
    assert response.status_code == 200


def test_search_help(client):
    """测试搜索帮助内容"""
    response = client.get(
        "/api/v1/help/search", params={"keyword": "测试", "type": "all"}
    )
    assert response.status_code == 200


def test_get_popular_content(client):
    """测试获取热门内容"""
    response = client.get("/api/v1/help/popular")
    assert response.status_code == 200
    data = response.json()
    assert "articles" in data
    assert "faqs" in data
