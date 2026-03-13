import httpx
import pytest

from app.ai.deepseek_service import DeepSeekService, deepseek_service
from app.ai.openai_service import script_generator
from app.services.ai_provider_config_service import AIProviderConfigService


@pytest.mark.asyncio
async def test_deepseek_generate_uses_chat_completions(monkeypatch):
    service = DeepSeekService()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        AIProviderConfigService,
        "get_runtime_config",
        staticmethod(
            lambda force_refresh=False: {
                "deepseek": {
                    "api_key": "test-deepseek-key",
                    "api_base": "https://api.deepseek.com",
                    "model": "deepseek-chat",
                }
            }
        ),
    )

    async def fake_post(self, url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return httpx.Response(
            200,
            json={
                "model": "deepseek-chat",
                "choices": [{"message": {"content": "生成成功"}}],
                "usage": {"total_tokens": 123},
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    result = await service.generate(
        "请生成创作脚本",
        system_prompt="你是专业脚本助手",
        temperature=0.4,
        max_tokens=512,
    )

    assert result["content"] == "生成成功"
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["headers"] == {
        "Authorization": "Bearer test-deepseek-key",
        "Content-Type": "application/json",
    }
    assert captured["json"] == {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是专业脚本助手"},
            {"role": "user", "content": "请生成创作脚本"},
        ],
        "temperature": 0.4,
        "max_tokens": 512,
    }


@pytest.mark.asyncio
async def test_script_generator_delegates_to_deepseek(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_generate_script(*, keywords, output_type, style=None, scene_count=1, **kwargs):
        captured["keywords"] = keywords
        captured["output_type"] = output_type
        captured["style"] = style
        captured["scene_count"] = scene_count
        return {"script": "脚本内容"}

    monkeypatch.setattr(deepseek_service, "generate_script", fake_generate_script)

    result = await script_generator.generate_from_keywords(
        keywords="防晒, 海边, 夏日",
        output_type="video",
        style="清新",
        scene_count=3,
    )

    assert result == {"script": "脚本内容"}
    assert captured == {
        "keywords": "防晒, 海边, 夏日",
        "output_type": "video",
        "style": "清新",
        "scene_count": 3,
    }
