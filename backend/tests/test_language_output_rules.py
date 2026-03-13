import pytest

from app.ai.ad_service import AdDesignService
from app.ai.deepseek_service import DeepSeekService
from app.ai.language_utils import build_language_instruction, detect_primary_language


def test_detect_primary_language_prefers_chinese_for_chinese_input():
    assert detect_primary_language("请生成一个夏日防晒广告脚本") == "zh"


def test_detect_primary_language_prefers_english_for_english_input():
    assert detect_primary_language("Create a summer sunscreen ad script") == "en"


@pytest.mark.asyncio
async def test_generate_script_adds_chinese_output_contract(monkeypatch):
    service = DeepSeekService()
    captured: dict[str, str | None] = {}

    async def fake_generate(prompt: str, system_prompt: str | None = None, **kwargs):
        captured["prompt"] = prompt
        captured["system_prompt"] = system_prompt
        return {"content": "ok"}

    monkeypatch.setattr(service, "generate", fake_generate)

    await service.generate_script(
        keywords="请写一个防晒霜短视频脚本",
        output_type="video",
        style="清新",
        scene_count=3,
    )

    expected = build_language_instruction("请写一个防晒霜短视频脚本\n清新")
    assert expected in (captured["system_prompt"] or "")


@pytest.mark.asyncio
async def test_generate_script_adds_english_output_contract(monkeypatch):
    service = DeepSeekService()
    captured: dict[str, str | None] = {}

    async def fake_generate(prompt: str, system_prompt: str | None = None, **kwargs):
        captured["prompt"] = prompt
        captured["system_prompt"] = system_prompt
        return {"content": "ok"}

    monkeypatch.setattr(service, "generate", fake_generate)

    await service.generate_script(
        keywords="Write a product launch ad script",
        output_type="video",
        style="minimalist",
        scene_count=2,
    )

    expected = build_language_instruction("Write a product launch ad script\nminimalist")
    assert expected in (captured["system_prompt"] or "")


@pytest.mark.asyncio
async def test_ad_requirements_add_language_contract(monkeypatch):
    service = AdDesignService()
    captured: list[str] = []

    async def fake_openai_generate(prompt: str, **kwargs):
        captured.append(prompt)
        return {"content": "creative plan"}

    monkeypatch.setattr(service.openai, "generate", fake_openai_generate)

    await service.analyze_requirements(
        product_info="请为夏季防晒霜生成广告方案",
        target_audience="18-30岁女性",
        ad_type="image",
        brand_style="清新自然",
    )

    expected = build_language_instruction("请为夏季防晒霜生成广告方案\n18-30岁女性\n清新自然")
    assert any(expected in prompt for prompt in captured)
