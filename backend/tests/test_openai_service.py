import pytest

from app.ai.openai_service import OpenAIService


@pytest.mark.asyncio
async def test_script_prompts_keep_expected_chinese_copy(monkeypatch):
    service = OpenAIService()
    captured = []

    async def fake_generate(prompt: str, system_prompt: str | None = None, **kwargs):
        captured.append({"prompt": prompt, "system_prompt": system_prompt})
        return {"content": "ok"}

    monkeypatch.setattr(service, "generate", fake_generate)

    await service.generate_script(
        keywords="防晒, 海边, 年轻女性",
        output_type="video",
        style="清新",
        scene_count=3,
    )
    await service.improve_script(
        original_script="原始脚本",
        improvements="加强节奏和镜头切换",
    )

    assert len(captured) == 2

    generate_call = captured[0]
    assert "创意脚本生成助手" in generate_call["system_prompt"]
    assert "请根据以下要求生成创作脚本" in generate_call["prompt"]
    assert "关键词：防晒, 海边, 年轻女性" in generate_call["prompt"]
    assert "输出类型：video" in generate_call["prompt"]
    assert "风格：清新" in generate_call["prompt"]
    assert "场景数量：3" in generate_call["prompt"]

    improve_call = captured[1]
    assert "脚本优化助手" in improve_call["system_prompt"]
    assert "请优化以下脚本" in improve_call["prompt"]
    assert "原始脚本：原始脚本" in improve_call["prompt"]
    assert "改进要求：加强节奏和镜头切换" in improve_call["prompt"]
