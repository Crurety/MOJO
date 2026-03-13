from app.models import Message, Task, Work
from app.tasks import content_tasks


def test_process_content_task_script_success(db, test_user, monkeypatch):
    user_id = test_user.id
    task = Task(
        user_id=user_id,
        task_no="SCRIPT001",
        task_type="script",
        status=0,
        progress=0,
        parameters={"keywords": "launch", "output_type": "video"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_process_script_task(_task):
        return {"script": "launch script"}

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks, "process_script_task", fake_process_script_task)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        messages = verify_db.query(Message).filter(Message.user_id == user_id).all()

        assert result["status"] == "success"
        assert result["result"]["script"] == "launch script"
        assert saved_task.status == 2
        assert saved_task.progress == 100
        assert len(messages) == 1
    finally:
        verify_db.close()


def test_process_content_task_image_success_creates_work(db, test_user, monkeypatch):
    task = Task(
        user_id=test_user.id,
        task_no="IMAGE001",
        task_type="image",
        status=0,
        progress=0,
        parameters={"prompt": "cat"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_process_image_task(_task):
        return {"images": ["/uploads/images/cat.png"], "count": 1}

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks, "process_image_task", fake_process_image_task)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        work = verify_db.query(Work).filter(Work.task_id == task_id).first()

        assert result["status"] == "success"
        assert saved_task.status == 2
        assert saved_task.result_url == "/uploads/images/cat.png"
        assert work is not None
        assert work.file_url == "/uploads/images/cat.png"
    finally:
        verify_db.close()


def test_process_content_task_video_processing_branch(db, test_user, monkeypatch):
    task = Task(
        user_id=test_user.id,
        task_no="VIDEO001",
        task_type="video",
        status=0,
        progress=0,
        parameters={"prompt": "teaser"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_process_video_task(_task):
        return {"external_task_id": "ext-1", "status": "pending", "result_url": None}

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks, "process_video_task", fake_process_video_task)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()

        assert result["status"] == "processing"
        assert saved_task.status == 1
        assert saved_task.progress == 60
        assert saved_task.parameters["external_task_id"] == "ext-1"
    finally:
        verify_db.close()


def test_process_content_task_ad_image_success(db, test_user, monkeypatch):
    task = Task(
        user_id=test_user.id,
        task_no="AD001",
        task_type="ad",
        status=0,
        progress=0,
        parameters={"ad_type": "image"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_process_ad_task(_task):
        return {"ad_type": "image", "images": ["/uploads/ads/ad.png"]}

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks, "process_ad_task", fake_process_ad_task)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        work = verify_db.query(Work).filter(Work.task_id == task_id).first()

        assert result["status"] == "success"
        assert saved_task.status == 2
        assert saved_task.result_url == "/uploads/ads/ad.png"
        assert work is not None
    finally:
        verify_db.close()


def test_process_content_task_unknown_type_marks_failed(db, test_user, monkeypatch):
    task = Task(
        user_id=test_user.id,
        task_no="UNKNOWN001",
        task_type="unknown",
        status=0,
        progress=0,
        parameters={},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        assert result == {"status": "error", "message": "Unknown task type"}
        assert saved_task.status == 3
        assert saved_task.error_message == "Unknown task type"
    finally:
        verify_db.close()


def test_process_content_task_exception_marks_failed_and_notifies(db, test_user, monkeypatch):
    user_id = test_user.id
    task = Task(
        user_id=user_id,
        task_no="FAIL001",
        task_type="image",
        status=0,
        progress=0,
        parameters={"prompt": "broken"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_process_image_task(_task):
        raise RuntimeError("provider crashed")

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks, "process_image_task", fake_process_image_task)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        messages = verify_db.query(Message).filter(Message.user_id == user_id).all()

        assert result == {"status": "error", "message": "provider crashed"}
        assert saved_task.status == 3
        assert saved_task.error_message == "provider crashed"
        assert len(messages) == 1
    finally:
        verify_db.close()



def test_process_content_task_video_missing_result_marks_failed(db, test_user, monkeypatch):
    user_id = test_user.id
    task = Task(
        user_id=user_id,
        task_no="VIDFAIL001",
        task_type="video",
        status=0,
        progress=0,
        parameters={"prompt": "broken video"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_process_video_task(_task):
        return {"status": "completed", "result_url": None, "external_task_id": None}

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks, "process_video_task", fake_process_video_task)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        messages = verify_db.query(Message).filter(Message.user_id == user_id).all()

        assert result == {"status": "error", "message": "Generation returned neither an external task ID nor a result URL."}
        assert saved_task.status == 3
        assert saved_task.error_message == "Generation returned neither an external task ID nor a result URL."
        assert len(messages) == 1
    finally:
        verify_db.close()


def test_check_video_status_completed_without_result_url_marks_failed(db, test_user, monkeypatch):
    user_id = test_user.id
    task = Task(
        user_id=user_id,
        task_no="VIDPOLL001",
        task_type="video",
        status=1,
        progress=60,
        parameters={"external_task_id": "ext-123"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_get_status(_task_id):
        return {"status": "completed", "result_url": None}

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks.video_generator, "get_status", fake_get_status)

    result = content_tasks.check_video_status.run()

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        messages = verify_db.query(Message).filter(Message.user_id == user_id).all()

        assert result == {"checked_count": 1}
        assert saved_task.status == 3
        assert saved_task.error_message == "Generation completed without a result URL."
        assert len(messages) == 1
    finally:
        verify_db.close()



def test_process_content_task_ad_image_missing_result_marks_failed(db, test_user, monkeypatch):
    user_id = test_user.id
    task = Task(
        user_id=user_id,
        task_no="ADFAIL001",
        task_type="ad",
        status=0,
        progress=0,
        parameters={"ad_type": "image"},
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id

    async def fake_process_ad_task(_task):
        return {"ad_type": "image", "images": []}

    monkeypatch.setattr(content_tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(content_tasks, "process_ad_task", fake_process_ad_task)

    result = content_tasks.process_content_task.run(task_id)

    verify_db = db.info["session_factory"]()
    try:
        saved_task = verify_db.query(Task).filter(Task.id == task_id).first()
        messages = verify_db.query(Message).filter(Message.user_id == user_id).all()

        assert result == {"status": "error", "message": "Ad image generation returned no images."}
        assert saved_task.status == 3
        assert saved_task.error_message == "Ad image generation returned no images."
        assert len(messages) == 1
    finally:
        verify_db.close()
