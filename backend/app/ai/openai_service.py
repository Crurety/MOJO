from __future__ import annotations

from typing import Any, Dict

import httpx

from app.ai.base import BaseAIService
from app.services.ai_provider_config_service import AIProviderConfigService


class OpenAIService(BaseAIService):
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        runtime = AIProviderConfigService.get_runtime_config().get("openai", {})
        api_key = runtime.get("api_key", "")
        base_url = (runtime.get("api_base") or "https://api.openai.com/v1").rstrip("/")
        model = runtime.get("model") or "gpt-4"

        if not api_key:
            raise Exception("OpenAI API key is not configured")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60.0,
            )

            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")

            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
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
        system_prompt = (
            "你是一个专业的创意脚本生成助手。请根据关键词生成结构化创作脚本，"
            "覆盖主题、场景、镜头和风格建议。"
        )
        prompt = f"""请根据以下要求生成创作脚本：

关键词：{keywords}
输出类型：{output_type}
风格：{style or "自然"}
场景数量：{scene_count}

请直接返回可执行的脚本文本。"""

        result = await self.generate(prompt, system_prompt=system_prompt)
        return {
            "script": result["content"],
            "keywords": keywords,
            "output_type": output_type,
            "style": style,
            "scene_count": scene_count,
        }

    async def improve_script(self, original_script: str, improvements: str) -> Dict[str, Any]:
        system_prompt = "你是专业脚本优化助手，请根据改进意见优化原始脚本。"
        prompt = f"""请优化以下脚本：

原始脚本：
{original_script}

改进要求：
{improvements}

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


class ScriptGenerator:
    def __init__(self):
        self.openai = OpenAIService()

    async def generate_from_keywords(
        self,
        keywords: str,
        output_type: str,
        style: str | None = None,
        scene_count: int = 1,
    ) -> Dict[str, Any]:
        return await self.openai.generate_script(
            keywords=keywords,
            output_type=output_type,
            style=style,
            scene_count=scene_count,
        )

    async def generate_from_answers(self, answers: Dict[str, Any], output_type: str) -> Dict[str, Any]:
        keywords = ", ".join([f"{k}: {v}" for k, v in answers.items()])
        return await self.openai.generate_script(keywords=keywords, output_type=output_type)

    async def improve(self, original_script: str, improvements: str) -> Dict[str, Any]:
        return await self.openai.improve_script(original_script, improvements)


openai_service = OpenAIService()
script_generator = ScriptGenerator()

