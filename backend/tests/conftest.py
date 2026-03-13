"""Shared pytest fixtures."""

import os
import shutil
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure app package is importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Disable DB table auto-create side effects and keep tests deterministic.
os.environ["TESTING"] = "true"
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./pytest-bootstrap.db")

# Disable rate-limit decorators in tests.
from app.core import rate_limit

rate_limit.limiter.limit = lambda *args, **kwargs: lambda f: f

from app.core.database import get_db
from app.core.security import get_password_hash
from app.main import app
from app.models import Message, Order, Script, Task, User, UserPermission, Work
from app.models.base import Base

TEST_DB_ROOT = Path(__file__).resolve().parent / ".tmp_dbs"
TEST_DB_ROOT.mkdir(exist_ok=True)


@pytest.fixture(scope="function")
def db():
    db_dir = TEST_DB_ROOT / str(uuid4())
    db_dir.mkdir()
    db_path = db_dir / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    session.info["session_factory"] = testing_session_local
    session.info["db_dir"] = db_dir
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        shutil.rmtree(db_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        session = db.info["session_factory"]()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        phone="13800138000",
        password=get_password_hash("Test123456"),
        nickname="test_user",
        status=1,
        balance=Decimal("100.00"),
        invite_code="TESTCODE",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user2(db):
    user = User(
        email="test2@example.com",
        phone="13900139000",
        password=get_password_hash("Test123456"),
        nickname="test_user_2",
        status=1,
        balance=Decimal("50.00"),
        invite_code="TESTCODE2",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def disabled_user(db):
    user = User(
        email="disabled@example.com",
        phone="13700137000",
        password=get_password_hash("Test123456"),
        nickname="disabled_user",
        status=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    user = User(
        email="admin@example.com",
        phone="13600136000",
        password=get_password_hash("Admin123456"),
        nickname="admin_user",
        status=1,
        balance=Decimal("0.00"),
        invite_code="ADMIN001",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"account": "test@example.com", "password": "Test123456"},
    )
    assert response.status_code == 200
    token = response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"account": "admin@example.com", "password": "Admin123456"},
    )
    assert response.status_code == 200
    token = response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_permission(db, test_user):
    perm = UserPermission(
        user_id=test_user.id,
        permission_type="script",
        payment_mode="per_use",
        total_count=10,
        used_count=0,
        status=1,
    )
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


@pytest.fixture
def test_order(db, test_user):
    order = Order(
        user_id=test_user.id,
        order_no="O20260305TEST001",
        order_type="permission",
        product_name="script-per_use",
        amount=Decimal("10.00"),
        status=0,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture
def paid_order(db, test_user):
    order = Order(
        user_id=test_user.id,
        order_no="O20260305PAID001",
        order_type="permission",
        product_name="image-monthly",
        amount=Decimal("99.00"),
        payment_method="alipay",
        status=1,
        paid_at=datetime.now(),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture
def test_task(db, test_user):
    task = Task(
        user_id=test_user.id,
        task_no="T20260305TEST001",
        task_type="image",
        status=0,
        progress=0,
        parameters={"prompt": "a cute cat", "clarity": "1080p"},
        cost_amount=3,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def completed_task(db, test_user):
    task = Task(
        user_id=test_user.id,
        task_no="T20260305DONE001",
        task_type="image",
        status=2,
        progress=100,
        parameters={"prompt": "sunset landscape"},
        result_url="https://storage.example.com/result.png",
        cost_amount=3,
        completed_at=datetime.now(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def test_work(db, test_user, completed_task):
    work = Work(
        user_id=test_user.id,
        task_id=completed_task.id,
        work_type="image",
        title="test_work",
        file_url="https://storage.example.com/work.png",
        thumbnail_url="https://storage.example.com/thumb.png",
        parameters={"style": "realistic"},
        is_public=1,
        quality_score=85,
    )
    db.add(work)
    db.commit()
    db.refresh(work)
    return work


@pytest.fixture
def test_script(db, test_user):
    script = Script(
        user_id=test_user.id,
        title="test_script",
        content="test content",
        output_type="video",
        parameters={"style": "sci-fi"},
        status=1,
    )
    db.add(script)
    db.commit()
    db.refresh(script)
    return script


@pytest.fixture
def test_message(db, test_user):
    msg = Message(
        user_id=test_user.id,
        title="test_notification",
        content="task completed",
        message_type="task",
        is_read=0,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@pytest.fixture
def multiple_messages(db, test_user):
    messages = []
    for i in range(5):
        msg = Message(
            user_id=test_user.id,
            title=f"message_{i + 1}",
            content=f"content_{i + 1}",
            message_type="system" if i % 2 == 0 else "task",
            is_read=0 if i < 3 else 1,
        )
        db.add(msg)
        messages.append(msg)
    db.commit()
    return messages
