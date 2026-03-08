from __future__ import annotations

import uuid
from typing import Any, Dict

import httpx

from app.ai.base import BaseAIService
from app.services.ai_provider_config_service import AIProviderConfigService


class RunwayService(BaseAIService):
    async def generate(
        self,
        prompt: str,
        duration: int = 4,
        resolution: str = "1080p",
        fps: int = 24,
        style: str | None = None,
        **kwargs,
    ) -> Dict[str, Any]:
        runtime = AIProviderConfigService.get_runtime_config().get("runway", {})
        api_key = runtime.get("api_key", "")
        base_url = (runtime.get("api_base") or "https://api.runwayml.com/v1").rstrip("/")

        if not api_key:
            raise Exception("Runway API key is not configured")

        fallback_task_id = str(uuid.uuid4())
        payload = {
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "fps": fps,
            "style": style,
            "callback_url": kwargs.get("callback_url"),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/generate",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30.0,
            )

            if response.status_code not in (200, 201):
                raise Exception(f"Runway API error: {response.text}")

            data = response.json()
            return {
                "task_id": data.get("id", fallback_task_id),
                "status": data.get("status", "pending"),
                "estimated_time": data.get("estimated_time", duration * 10),
                "result_url": data.get("result_url"),
            }

    async def generate_from_script(
        self,
        script: Dict[str, Any],
        duration: int = 4,
        clarity: str = "1080p",
        style: str | None = None,
    ) -> Dict[str, Any]:
        prompt = script.get("script", str(script))
        if style:
            prompt = f"{prompt}, {style} style"

        return await self.generate(
            prompt=prompt,
            duration=duration,
            resolution=clarity,
            style=style,
        )

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        runtime = AIProviderConfigService.get_runtime_config().get("runway", {})
        api_key = runtime.get("api_key", "")
        base_url = (runtime.get("api_base") or "https://api.runwayml.com/v1").rstrip("/")

        if not api_key:
            raise Exception("Runway API key is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0,
            )

            if response.status_code != 200:
                raise Exception(f"Runway API error: {response.text}")

            data = response.json()
            return {
                "task_id": task_id,
                "status": data.get("status", "unknown"),
                "progress": data.get("progress", 0),
                "result_url": data.get("result_url"),
                "error": data.get("error"),
            }

    async def cancel(self, task_id: str) -> bool:
        runtime = AIProviderConfigService.get_runtime_config().get("runway", {})
        api_key = runtime.get("api_key", "")
        base_url = (runtime.get("api_base") or "https://api.runwayml.com/v1").rstrip("/")

        if not api_key:
            raise Exception("Runway API key is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/tasks/{task_id}/cancel",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0,
            )
            return response.status_code == 200


class VideoGenerator:
    def __init__(self):
        self.runway = RunwayService()

    async def generate(
        self,
        prompt: str,
        duration: int = 4,
        clarity: str = "1080p",
        style: str | None = None,
        **kwargs,
    ) -> Dict[str, Any]:
        return await self.runway.generate(
            prompt=prompt,
            duration=duration,
            resolution=clarity,
            style=style,
            **kwargs,
        )

    async def generate_from_script(
        self,
        script: Dict[str, Any],
        duration: int = 4,
        clarity: str = "1080p",
        style: str | None = None,
    ) -> Dict[str, Any]:
        return await self.runway.generate_from_script(
            script=script,
            duration=duration,
            clarity=clarity,
            style=style,
        )

    async def get_status(self, task_id: str) -> Dict[str, Any]:
        return await self.runway.get_status(task_id)

    async def cancel(self, task_id: str) -> bool:
        return await self.runway.cancel(task_id)


runway_service = RunwayService()
video_generator = VideoGenerator()

