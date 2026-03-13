import base64
import importlib

import pytest

stability_module = importlib.import_module("app.ai.stability_service")
from app.ai.stability_service import ImageGenerator, StabilityAIService
from app.tasks.content_tasks import process_image_task
from app.models import Task


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


class _FakeAsyncClient:
    def __init__(self, handler):
        self._handler = handler

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, headers=None, json=None, data=None, timeout=None):
        return self._handler(url=url, headers=headers, json=json, data=data, timeout=timeout)


@pytest.mark.asyncio
async def test_stability_generate_maps_request_and_response(monkeypatch):
    service = StabilityAIService()
    captured = {}

    def fake_runtime_config():
        return {
            "stability": {
                "api_key": "test-key",
                "api_base": "https://stability.example/v1",
                "engine": "test-engine",
            }
        }

    def handler(**kwargs):
        captured.update(kwargs)
        return _FakeResponse(
            200,
            {
                "artifacts": [
                    {"base64": "abc", "seed": 123, "finishReason": "SUCCESS"},
                ],
                "seed": 456,
            },
        )

    monkeypatch.setattr(stability_module.AIProviderConfigService, "get_runtime_config", staticmethod(fake_runtime_config))
    monkeypatch.setattr(stability_module.httpx, "AsyncClient", lambda: _FakeAsyncClient(handler))

    result = await service.generate(
        prompt="sunset beach",
        negative_prompt="blurry",
        width=512,
        height=512,
        steps=20,
        cfg_scale=6.5,
        seed=99,
        style_preset="photographic",
    )

    assert captured["url"] == "https://stability.example/v1/generation/test-engine/text-to-image"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["text_prompts"][0] == {"text": "sunset beach", "weight": 1.0}
    assert captured["json"]["text_prompts"][1] == {"text": "blurry", "weight": -1.0}
    assert captured["json"]["width"] == 512
    assert captured["json"]["height"] == 512
    assert captured["json"]["style_preset"] == "photographic"
    assert result == {
        "images": [{"base64": "abc", "seed": 123, "finish_reason": "SUCCESS"}],
        "seed": 456,
    }


@pytest.mark.asyncio
async def test_stability_generate_raises_on_non_200(monkeypatch):
    service = StabilityAIService()

    monkeypatch.setattr(
        stability_module.AIProviderConfigService,
        "get_runtime_config",
        staticmethod(lambda: {"stability": {"api_key": "test-key", "api_base": "https://stability.example/v1", "engine": "test-engine"}}),
    )
    monkeypatch.setattr(
        stability_module.httpx,
        "AsyncClient",
        lambda: _FakeAsyncClient(lambda **kwargs: _FakeResponse(500, {"error": "bad gateway"})),
    )

    with pytest.raises(Exception, match="Stability API error"):
        await service.generate(prompt="sunset")


@pytest.mark.asyncio
async def test_stability_generate_from_script_respects_clarity_and_count(monkeypatch):
    service = StabilityAIService()
    calls = []

    async def fake_generate(**kwargs):
        calls.append(kwargs)
        return {"images": [{"base64": f"img-{len(calls)}"}]}

    monkeypatch.setattr(service, "generate", fake_generate)

    result = await service.generate_from_script(
        script={"script": "city skyline"},
        clarity="4k",
        style="anime",
        count=2,
    )

    assert len(calls) == 2
    assert calls[0]["prompt"] == "city skyline, anime style"
    assert calls[0]["width"] == 2048
    assert calls[0]["height"] == 1152
    assert calls[0]["style_preset"] == "anime"
    assert result["count"] == 2
    assert result["clarity"] == "4k"
    assert result["style"] == "anime"


@pytest.mark.asyncio
async def test_stability_image_to_image_maps_response(monkeypatch):
    service = StabilityAIService()
    captured = {}

    monkeypatch.setattr(
        stability_module.AIProviderConfigService,
        "get_runtime_config",
        staticmethod(lambda: {"stability": {"api_key": "test-key", "api_base": "https://stability.example/v1", "engine": "test-engine"}}),
    )

    def handler(**kwargs):
        captured.update(kwargs)
        return _FakeResponse(200, {"artifacts": [{"base64": "ref-image", "seed": 321}]})

    monkeypatch.setattr(stability_module.httpx, "AsyncClient", lambda: _FakeAsyncClient(handler))

    result = await service.image_to_image(
        init_image="base64-ref",
        prompt="make it cinematic",
        image_strength=0.4,
        cfg_scale=8,
    )

    assert captured["url"] == "https://stability.example/v1/generation/test-engine/image-to-image"
    assert captured["data"]["text_prompts[0][text]"] == "make it cinematic"
    assert captured["data"]["init_image"] == "base64-ref"
    assert captured["data"]["image_strength"] == 0.4
    assert captured["data"]["cfg_scale"] == 8
    assert result == {"images": [{"base64": "ref-image", "seed": 321}]}


@pytest.mark.asyncio
async def test_image_generator_delegates_to_stability(monkeypatch):
    generator = ImageGenerator()

    async def fake_generate_from_script(**kwargs):
        return {"images": [{"base64": "img"}], "count": 1}

    async def fake_image_to_image(**kwargs):
        return {"images": [{"base64": "ref"}]}

    monkeypatch.setattr(generator.stability, "generate_from_script", fake_generate_from_script)
    monkeypatch.setattr(generator.stability, "image_to_image", fake_image_to_image)

    single = await generator.generate_single(prompt="hero shot", clarity="720p", style="photo", count=2)
    scripted = await generator.generate_from_script(script={"script": "hero shot"}, clarity="1080p", style="photo", count=1)
    referenced = await generator.generate_with_reference(reference_image="ref", prompt="hero shot", image_strength=0.5)

    assert single == {"images": [{"base64": "img"}]}
    assert scripted == {"images": [{"base64": "img"}], "count": 1}
    assert referenced == {"images": [{"base64": "ref"}]}
    assert await generator.stability.get_status("task-1") == {"status": "completed", "task_id": "task-1"}
    assert await generator.stability.cancel("task-1") is True


@pytest.mark.asyncio
async def test_process_image_task_saves_generated_images(monkeypatch):
    png_bytes = base64.b64encode(b"fake-image-bytes").decode()
    saved = []

    async def fake_generate_single(**kwargs):
        return {"images": [{"base64": png_bytes}, {"base64": png_bytes}]}

    async def fake_save_file(file_content, file_extension, sub_dir=""):
        saved.append((file_content, file_extension, sub_dir))
        return f"{sub_dir}/generated-{len(saved)}.png"

    monkeypatch.setattr("app.tasks.content_tasks.image_generator.generate_single", fake_generate_single)
    monkeypatch.setattr("app.tasks.content_tasks.storage_service.save_file", fake_save_file)
    monkeypatch.setattr("app.tasks.content_tasks.storage_service.get_file_url", lambda path: f"/uploads/{path}")

    task = Task(task_type="image", parameters={"prompt": "a castle", "clarity": "1080p", "style": "fantasy", "count": 2})

    result = await process_image_task(task)

    assert result == {
        "images": ["/uploads/images/generated-1.png", "/uploads/images/generated-2.png"],
        "count": 2,
    }
    assert len(saved) == 2
    assert all(item[1] == ".png" for item in saved)
    assert all(item[2] == "images" for item in saved)


@pytest.mark.asyncio
async def test_process_image_task_uses_reference_generator(monkeypatch):
    png_bytes = base64.b64encode(b"ref-image-bytes").decode()

    async def fake_generate_with_reference(**kwargs):
        return {"images": [{"base64": png_bytes}]}

    async def fake_save_file(file_content, file_extension, sub_dir=""):
        return "images/reference-result.png"

    monkeypatch.setattr("app.tasks.content_tasks.image_generator.generate_with_reference", fake_generate_with_reference)
    monkeypatch.setattr("app.tasks.content_tasks.storage_service.save_file", fake_save_file)
    monkeypatch.setattr("app.tasks.content_tasks.storage_service.get_file_url", lambda path: f"/uploads/{path}")

    task = Task(task_type="image", parameters={"prompt": "enhance portrait", "reference_image": "ref-data", "clarity": "720p"})

    result = await process_image_task(task)

    assert result == {"images": ["/uploads/images/reference-result.png"], "count": 1}
