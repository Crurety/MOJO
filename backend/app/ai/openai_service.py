from typing import Dict, Any, Optional, List
from app.ai.base import BaseAIService
from app.core.config import settings
import httpx
import json


class OpenAIService(BaseAIService):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_API_BASE or "https://api.openai.com/v1"
        self.model = settings.OPENAI_MODEL or "gpt-4"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.text}")
            
            data = response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "model": data.get("model", self.model)
            }
    
    async def generate_script(
        self,
        keywords: str,
        output_type: str = "image",
        style: str = None,
        scene_count: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        system_prompt = """你是一个专业的创意脚本生成助手。根据用户提供的关键词和要求，生成详细的创作脚本。
脚本应该包含：
1. 主题和风格描述
2. 场景描述（如果是视频或图片集）
3. 具体的视觉元素建议
4. 色调和氛围建议

请以JSON格式返回结果。"""
        
        prompt = f"""请根据以下要求生成创作脚本：

关键词：{keywords}
输出类型：{output_type}
风格：{style or '自然'}
场景数量：{scene_count}

请生成一个完整的创作脚本，包含场景描述、视觉元素、色调建议等。"""
        
        result = await self.generate(prompt, system_prompt=system_prompt)
        
        return {
            "script": result["content"],
            "keywords": keywords,
            "output_type": output_type,
            "style": style,
            "scene_count": scene_count
        }
    
    async def improve_script(
        self,
        original_script: str,
        improvements: str
    ) -> Dict[str, Any]:
        system_prompt = "你是一个专业的创意脚本优化助手。根据用户的改进要求，优化原始脚本。"
        
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
            "improvements": improvements
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
        style: str = None,
        scene_count: int = 1
    ) -> Dict[str, Any]:
        return await self.openai.generate_script(
            keywords=keywords,
            output_type=output_type,
            style=style,
            scene_count=scene_count
        )
    
    async def generate_from_answers(
        self,
        answers: Dict[str, Any],
        output_type: str
    ) -> Dict[str, Any]:
        keywords = ", ".join([f"{k}: {v}" for k, v in answers.items()])
        return await self.openai.generate_script(
            keywords=keywords,
            output_type=output_type
        )
    
    async def improve(
        self,
        original_script: str,
        improvements: str
    ) -> Dict[str, Any]:
        return await self.openai.improve_script(original_script, improvements)


openai_service = OpenAIService()
script_generator = ScriptGenerator()
