"""广告设计服务"""
from typing import Dict, Any, List, Optional
from app.ai.openai_service import openai_service
from app.ai.stability_service import image_generator
from app.ai.runway_service import video_generator


class AdDesignService:
    """广告设计服务"""

    def __init__(self):
        self.openai = openai_service
        self.image_gen = image_generator
        self.video_gen = video_generator

    async def generate_from_script(
        self,
        script: Dict[str, Any],
        ad_type: str = "image",
        materials: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """根据脚本生成广告

        Args:
            script: 创作脚本
            ad_type: 广告类型 (image/video)
            materials: 用户提供的素材URL列表

        Returns:
            Dict: 广告设计结果
        """
        # 生成广告创意方案
        creative_plan = await self._generate_creative_plan(script, ad_type, materials)

        if ad_type == "image":
            result = await self._generate_image_ad(creative_plan, materials)
        elif ad_type == "video":
            result = await self._generate_video_ad(creative_plan, materials)
        else:
            raise ValueError(f"不支持的广告类型: {ad_type}")

        return {
            "ad_type": ad_type,
            "creative_plan": creative_plan,
            "result": result
        }

    async def generate_from_materials(
        self,
        materials: List[str],
        ad_type: str = "image",
        requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """根据素材组合生成广告

        Args:
            materials: 素材URL列表
            ad_type: 广告类型 (image/video)
            requirements: 额外要求

        Returns:
            Dict: 广告设计结果
        """
        # 分析素材并生成创意方案
        creative_plan = await self._analyze_materials_and_plan(materials, ad_type, requirements)

        if ad_type == "image":
            result = await self._generate_image_ad(creative_plan, materials)
        elif ad_type == "video":
            result = await self._generate_video_ad(creative_plan, materials)
        else:
            raise ValueError(f"不支持的广告类型: {ad_type}")

        return {
            "ad_type": ad_type,
            "creative_plan": creative_plan,
            "result": result,
            "materials_used": materials
        }

    async def _generate_creative_plan(
        self,
        script: Dict[str, Any],
        ad_type: str,
        materials: Optional[List[str]] = None
    ) -> str:
        """生成广告创意方案

        Args:
            script: 创作脚本
            ad_type: 广告类型
            materials: 素材列表

        Returns:
            str: 创意方案文本
        """
        system_prompt = """你是一个专业的广告创意设计师。
根据提供的脚本和素材，生成详细的广告创意方案。
方案应包含：
1. 广告主题和核心信息
2. 视觉布局建议
3. 文案建议
4. 色彩和风格建议
5. 素材使用建议"""

        script_content = script.get("script", str(script))
        materials_info = f"\n可用素材数量: {len(materials)}" if materials else "\n无预设素材"

        prompt = f"""请为以下内容生成广告创意方案：

脚本内容：
{script_content}

广告类型：{ad_type}
{materials_info}

请生成详细的创意方案。"""

        result = await self.openai.generate(prompt, system_prompt=system_prompt)
        return result["content"]

    async def _analyze_materials_and_plan(
        self,
        materials: List[str],
        ad_type: str,
        requirements: Optional[str] = None
    ) -> str:
        """分析素材并生成创意方案

        Args:
            materials: 素材列表
            ad_type: 广告类型
            requirements: 额外要求

        Returns:
            str: 创意方案文本
        """
        system_prompt = """你是一个专业的广告创意设计师。
根据提供的素材和要求，生成详细的广告创意方案。
方案应包含：
1. 素材组合建议
2. 广告主题和核心信息
3. 视觉布局建议
4. 文案建议
5. 转场和动效建议（如果是视频）"""

        materials_info = f"素材数量: {len(materials)}"
        requirements_info = f"\n额外要求: {requirements}" if requirements else ""

        prompt = f"""请为以下素材生成广告创意方案：

{materials_info}
广告类型：{ad_type}
{requirements_info}

请生成详细的创意方案，说明如何组合这些素材。"""

        result = await self.openai.generate(prompt, system_prompt=system_prompt)
        return result["content"]

    async def _generate_image_ad(
        self,
        creative_plan: str,
        materials: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """生成图文广告

        Args:
            creative_plan: 创意方案
            materials: 素材列表

        Returns:
            Dict: 生成结果
        """
        # 提取关键信息生成广告图片
        prompt = f"""根据以下创意方案生成广告图片：

{creative_plan}

要求：
- 视觉冲击力强
- 信息传达清晰
- 符合广告设计规范"""

        # 使用图片生成服务
        result = await self.image_gen.generate_single(
            prompt=prompt,
            clarity="1080p",
            style="advertising"
        )

        return {
            "type": "image",
            "images": result.get("images", []),
            "prompt": prompt
        }

    async def _generate_video_ad(
        self,
        creative_plan: str,
        materials: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """生成视频广告

        Args:
            creative_plan: 创意方案
            materials: 素材列表

        Returns:
            Dict: 生成结果
        """
        # 提取关键信息生成广告视频
        prompt = f"""根据以下创意方案生成广告视频：

{creative_plan}

要求：
- 节奏紧凑
- 信息传达清晰
- 视觉吸引力强
- 符合广告设计规范"""

        # 使用视频生成服务
        result = await self.video_gen.generate(
            prompt=prompt,
            duration=15,  # 广告视频默认15秒
            clarity="1080p",
            style="advertising"
        )

        return {
            "type": "video",
            "task_id": result.get("task_id"),
            "status": result.get("status"),
            "prompt": prompt
        }

    async def optimize_ad(
        self,
        original_ad: Dict[str, Any],
        feedback: str
    ) -> Dict[str, Any]:
        """优化广告

        Args:
            original_ad: 原始广告数据
            feedback: 优化反馈

        Returns:
            Dict: 优化后的广告
        """
        system_prompt = "你是一个专业的广告优化师。根据反馈意见优化广告创意方案。"

        original_plan = original_ad.get("creative_plan", "")

        prompt = f"""请根据以下反馈优化广告方案：

原始方案：
{original_plan}

优化反馈：
{feedback}

请提供优化后的完整方案。"""

        result = await self.openai.generate(prompt, system_prompt=system_prompt)

        optimized_plan = result["content"]
        ad_type = original_ad.get("ad_type", "image")

        if ad_type == "image":
            new_result = await self._generate_image_ad(optimized_plan)
        else:
            new_result = await self._generate_video_ad(optimized_plan)

        return {
            "ad_type": ad_type,
            "creative_plan": optimized_plan,
            "result": new_result,
            "optimized": True
        }


ad_design_service = AdDesignService()
