import pytest

from app.ai.ad_service import AdDesignService


@pytest.mark.asyncio
async def test_ad_design_prompts_are_readable(monkeypatch):
    service = AdDesignService()
    captured = []

    async def fake_openai_generate(prompt: str, **kwargs):
        captured.append(prompt)
        return {"content": "creative plan"}

    async def fake_generate_image_ad(*args, **kwargs):
        return {"type": "image", "images": ["img"]}

    monkeypatch.setattr(service.openai, "generate", fake_openai_generate)
    monkeypatch.setattr(service, "generate_image_ad", fake_generate_image_ad)

    await service.analyze_requirements(
        product_info="Sparkling water for young professionals",
        target_audience="Urban professionals aged 25-35",
        ad_type="image",
        brand_style="minimalist",
    )
    await service._generate_creative_plan({"script": "Launch scene"}, "video", ["m1", "m2"])
    await service._analyze_materials_and_plan(["m1", "m2"], "image", "Focus on premium feel")
    await service.optimize_ad({"creative_plan": "Old plan", "ad_type": "image"}, "More energy")

    assert any("advertising creative director" in prompt.lower() for prompt in captured)
    assert any("execution-ready ad creative plan" in prompt for prompt in captured)
    assert any("Create an advertising creative plan based on the following input" in prompt for prompt in captured)
    assert any("Create an advertising creative plan from the following materials" in prompt for prompt in captured)
    assert any("Optimize the following advertising plan based on feedback" in prompt for prompt in captured)


@pytest.mark.asyncio
async def test_generate_image_ad_delegates_with_advertising_defaults(monkeypatch):
    service = AdDesignService()
    captured = {}

    async def fake_generate_single(**kwargs):
        captured.update(kwargs)
        return {"images": ["img-1"]}

    monkeypatch.setattr(service.image_gen, "generate_single", fake_generate_single)

    result = await service.generate_image_ad("Plan", clarity="720p")

    assert captured["clarity"] == "720p"
    assert captured["style"] == "advertising"
    assert captured["count"] == 1
    assert "high-converting advertising key visual" in captured["prompt"]
    assert result == {"type": "image", "images": ["img-1"], "prompt": captured["prompt"]}


@pytest.mark.asyncio
async def test_generate_video_ad_delegates_with_advertising_defaults(monkeypatch):
    service = AdDesignService()
    captured = {}

    async def fake_generate(**kwargs):
        captured.update(kwargs)
        return {"task_id": "vid-1", "status": "pending", "result_url": None}

    monkeypatch.setattr(service.video_gen, "generate", fake_generate)

    result = await service.generate_video_ad("Plan", duration=12, clarity="4k")

    assert captured["duration"] == 12
    assert captured["clarity"] == "4k"
    assert captured["style"] == "advertising"
    assert "short-form advertising video concept" in captured["prompt"]
    assert result["type"] == "video"
    assert result["task_id"] == "vid-1"


@pytest.mark.asyncio
async def test_generate_from_script_rejects_unsupported_ad_type():
    service = AdDesignService()

    with pytest.raises(ValueError, match="Unsupported ad type"):
        await service.generate_from_script({"script": "Plan"}, ad_type="audio")
