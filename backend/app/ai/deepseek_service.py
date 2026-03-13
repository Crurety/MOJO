from __future__ import annotations

from typing import Any, Dict

import httpx

from app.ai.base import BaseAIService
from app.ai.language_utils import build_language_instruction
from app.services.ai_provider_config_service import AIProviderConfigService


class DeepSeekService(BaseAIService):
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        runtime = AIProviderConfigService.get_runtime_config().get("deepseek", {})
        api_key = (runtime.get("api_key") or "").strip()
        base_url = (runtime.get("api_base") or "https://api.deepseek.com").rstrip("/")
        model = (runtime.get("model") or "deepseek-chat").strip()

        if not api_key:
            raise Exception("DeepSeek API key is not configured")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60.0,
            )

        if response.status_code != 200:
            raise Exception(f"DeepSeek API error: {response.text}")

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            raise Exception("DeepSeek API error: empty response content")

        return {
            "content": content,
            "usage": data.get("usage", {}),
            "model": data.get("model", model),
        }

    async def generate_script(
        self,
        keywords: str,
        output_type: str = "image",
        style: str | None = None,
        scene_count: int = 1,
        **kwargs,
    ) -> Dict[str, Any]:
        language_instruction = build_language_instruction("\n".join(part for part in [keywords, style or ""] if part))
        system_prompt = (
            "你是专业的创意脚本生成助手。"
            "请基于关键词生成结构化、可直接执行的创作脚本，覆盖主题、分镜、镜头和风格建议。"
            f" {language_instruction}"
        )
        prompt = f"""请根据以下要求生成创作脚本：

关键词：{keywords}
输出类型：{output_type}
风格：{style or "自然"}
场景数量：{scene_count}

语言要求：{language_instruction}

请直接返回完整脚本文本，尽量包含：
1. 脚本主题与创意方向
2. 分场景描述
3. 每个场景的镜头建议
4. 画面风格与节奏建议"""

        result = await self.generate(prompt, system_prompt=system_prompt)
        return {
            "script": result["content"],
            "keywords": keywords,
            "output_type": output_type,
            "style": style,
            "scene_count": scene_count,
        }

    async def improve_script(self, original_script: str, improvements: str) -> Dict[str, Any]:
        language_instruction = build_language_instruction(
            "\n".join(part for part in [original_script, improvements] if part)
        )
        system_prompt = f"你是专业的脚本优化助手，请根据修改意见优化原始脚本。 {language_instruction}"
        prompt = f"""请优化以下脚本：

原始脚本：{original_script}

优化要求：{improvements}

语言要求：{language_instruction}

请返回优化后的完整脚本。"""
        result = await self.generate(prompt, system_prompt=system_prompt)
        return {
            "improved_script": result["content"],
            "original_script": original_script,
            "improvements": improvements,
        }

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        return {"status": "completed", "task_id": task_id}

    async def cancel(self, task_id: str) -> bool:
        return True


deepseek_service = DeepSeekService()
