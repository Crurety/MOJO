from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.ai.language_utils import build_language_instruction
from app.ai.openai_service import openai_service
from app.ai.runway_service import video_generator
from app.ai.stability_service import image_generator


class AdDesignService:
    def __init__(self):
        self.openai = openai_service
        self.image_gen = image_generator
        self.video_gen = video_generator

    async def analyze_requirements(
        self,
        product_info: str,
        target_audience: str,
        ad_type: str = "image",
        brand_style: str | None = None,
    ) -> str:
        language_instruction = build_language_instruction(
            "\n".join(part for part in [product_info, target_audience, brand_style or ""] if part)
        )
        prompt = f"""You are an advertising creative director.
Analyze the following inputs and produce an execution-ready ad creative plan.
{language_instruction}

Product information: {product_info}
Target audience: {target_audience}
Ad type: {ad_type}
Brand style: {brand_style or "not specified"}

Return:
1. Core message and selling points
2. Visual or shot direction
3. Copy suggestions
4. CTA suggestions"""
        result = await self.openai.generate(prompt)
        return result["content"]

    async def generate_image_ad(
        self,
        creative_plan: str,
        clarity: str = "1080p",
        style: str | None = None,
        materials: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        language_instruction = build_language_instruction(creative_plan)
        prompt = f"""Create a high-converting advertising key visual based on the following creative plan.
Use the plan to produce a polished image generation prompt.
{language_instruction}

Creative plan:
{creative_plan}

Requirements:
- strong visual hook
- clear information hierarchy
- suitable for paid media placement"""

        result = await self.image_gen.generate_single(
            prompt=prompt,
            clarity=clarity,
            style=style or "advertising",
            count=1,
        )
        return {"type": "image", "images": result.get("images", []), "prompt": prompt}

    async def generate_video_ad(
        self,
        creative_plan: str,
        duration: int = 15,
        clarity: str = "1080p",
        style: str | None = None,
        materials: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        language_instruction = build_language_instruction(creative_plan)
        prompt = f"""Create a short-form advertising video concept based on the following creative plan.
Use the plan to produce a concise video generation prompt.
{language_instruction}

Creative plan:
{creative_plan}

Requirements:
- tight pacing
- clear message delivery
- strong call to action"""

        result = await self.video_gen.generate(
            prompt=prompt,
            duration=duration,
            clarity=clarity,
            style=style or "advertising",
        )
        return {
            "type": "video",
            "task_id": result.get("task_id"),
            "status": result.get("status"),
            "result_url": result.get("result_url"),
            "prompt": prompt,
        }

    async def generate_from_script(
        self,
        script: Dict[str, Any],
        ad_type: str = "image",
        materials: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if ad_type not in {"image", "video"}:
            raise ValueError(f"Unsupported ad type: {ad_type}")

        creative_plan = await self._generate_creative_plan(script, ad_type, materials)
        if ad_type == "image":
            result = await self.generate_image_ad(creative_plan=creative_plan, materials=materials)
        else:
            result = await self.generate_video_ad(creative_plan=creative_plan, materials=materials)

        return {"ad_type": ad_type, "creative_plan": creative_plan, "result": result}

    async def generate_from_materials(
        self,
        materials: List[str],
        ad_type: str = "image",
        requirements: Optional[str] = None,
    ) -> Dict[str, Any]:
        if ad_type not in {"image", "video"}:
            raise ValueError(f"Unsupported ad type: {ad_type}")

        creative_plan = await self._analyze_materials_and_plan(materials, ad_type, requirements)
        if ad_type == "image":
            result = await self.generate_image_ad(creative_plan=creative_plan, materials=materials)
        else:
            result = await self.generate_video_ad(creative_plan=creative_plan, materials=materials)

        return {
            "ad_type": ad_type,
            "creative_plan": creative_plan,
            "result": result,
            "materials_used": materials,
        }

    async def _generate_creative_plan(
        self,
        script: Dict[str, Any],
        ad_type: str,
        materials: Optional[List[str]] = None,
    ) -> str:
        script_content = script.get("script", str(script))
        materials_info = f"Available material count: {len(materials)}" if materials else "No predefined materials"
        language_instruction = build_language_instruction(script_content)
        prompt = f"""Create an advertising creative plan based on the following input.
{language_instruction}

Script content:
{script_content}

Ad type: {ad_type}
{materials_info}

Return a creative plan that can be used directly for design or generation."""
        result = await self.openai.generate(prompt)
        return result["content"]

    async def _analyze_materials_and_plan(
        self,
        materials: List[str],
        ad_type: str,
        requirements: Optional[str] = None,
    ) -> str:
        language_instruction = build_language_instruction(
            "\n".join(part for part in ["\n".join(materials), requirements or ""] if part)
        )
        prompt = f"""Create an advertising creative plan from the following materials.
{language_instruction}

Material count: {len(materials)}
Ad type: {ad_type}
Additional requirements: {requirements or "none"}

Return:
- recommended material combination
- visual direction
- copy angle
- CTA suggestion"""
        result = await self.openai.generate(prompt)
        return result["content"]

    async def optimize_ad(self, original_ad: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        original_plan = original_ad.get("creative_plan", "")
        language_instruction = build_language_instruction(
            "\n".join(part for part in [original_plan, feedback] if part)
        )
        prompt = f"""Optimize the following advertising plan based on feedback.
{language_instruction}

Original plan:
{original_plan}

Feedback:
{feedback}
"""
        result = await self.openai.generate(prompt)
        optimized_plan = result["content"]
        ad_type = original_ad.get("ad_type", "image")
        if ad_type == "image":
            new_result = await self.generate_image_ad(creative_plan=optimized_plan)
        else:
            new_result = await self.generate_video_ad(creative_plan=optimized_plan)

        return {
            "ad_type": ad_type,
            "creative_plan": optimized_plan,
            "result": new_result,
            "optimized": True,
        }


ad_design_service = AdDesignService()
