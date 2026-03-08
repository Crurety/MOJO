from __future__ import annotations

from typing import Any, Dict, List, Optional

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
        prompt = f"""你是一名广告创意总监，请根据以下输入输出可执行创意方案：

产品信息：{product_info}
目标人群：{target_audience}
广告类型：{ad_type}
品牌风格：{brand_style or "未指定"}

请输出：
1. 主诉求与卖点
2. 画面/镜头设计
3. 文案建议
4. 行动召唤建议"""
        result = await self.openai.generate(prompt)
        return result["content"]

    async def generate_image_ad(
        self,
        creative_plan: str,
        clarity: str = "1080p",
        style: str | None = None,
        materials: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        prompt = f"""请根据以下广告创意方案生成广告图像提示词并输出最终图像：
{creative_plan}

要求：
- 视觉冲击强
- 信息层级清晰
- 适合投放渠道"""

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
        prompt = f"""请根据以下广告创意方案生成视频广告：
{creative_plan}

要求：
- 节奏紧凑
- 信息传达清晰
- 突出行动召唤"""

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
        creative_plan = await self._generate_creative_plan(script, ad_type, materials)
        if ad_type == "image":
            result = await self.generate_image_ad(creative_plan=creative_plan, materials=materials)
        elif ad_type == "video":
            result = await self.generate_video_ad(creative_plan=creative_plan, materials=materials)
        else:
            raise ValueError(f"Unsupported ad type: {ad_type}")

        return {"ad_type": ad_type, "creative_plan": creative_plan, "result": result}

    async def generate_from_materials(
        self,
        materials: List[str],
        ad_type: str = "image",
        requirements: Optional[str] = None,
    ) -> Dict[str, Any]:
        creative_plan = await self._analyze_materials_and_plan(materials, ad_type, requirements)
        if ad_type == "image":
            result = await self.generate_image_ad(creative_plan=creative_plan, materials=materials)
        elif ad_type == "video":
            result = await self.generate_video_ad(creative_plan=creative_plan, materials=materials)
        else:
            raise ValueError(f"Unsupported ad type: {ad_type}")

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
        materials_info = f"可用素材数量: {len(materials)}" if materials else "无预设素材"
        prompt = f"""请根据以下内容生成广告创意方案：

脚本内容：
{script_content}

广告类型：{ad_type}
{materials_info}

请输出可直接用于设计/生成的创意方案。"""
        result = await self.openai.generate(prompt)
        return result["content"]

    async def _analyze_materials_and_plan(
        self,
        materials: List[str],
        ad_type: str,
        requirements: Optional[str] = None,
    ) -> str:
        prompt = f"""请为以下素材生成广告创意方案：

素材数量：{len(materials)}
广告类型：{ad_type}
额外要求：{requirements or "无"}

请输出素材组合建议、视觉布局、文案与行动召唤。"""
        result = await self.openai.generate(prompt)
        return result["content"]

    async def optimize_ad(self, original_ad: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        original_plan = original_ad.get("creative_plan", "")
        prompt = f"""请根据反馈优化广告方案：

原始方案：
{original_plan}

反馈：
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

