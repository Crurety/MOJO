from typing import Dict, Any, Optional, List
from app.ai.base import BaseAIService
from app.core.config import settings
import httpx
import uuid
import time


class RunwayService(BaseAIService):
    def __init__(self):
        self.api_key = settings.RUNWAY_API_KEY
        self.base_url = settings.RUNWAY_API_BASE or "https://api.runwayml.com/v1"
    
    async def generate(
        self,
        prompt: str,
        duration: int = 4,
        resolution: str = "1080p",
        fps: int = 24,
        style: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "duration": duration,
                    "resolution": resolution,
                    "fps": fps,
                    "style": style,
                    "callback_url": kwargs.get("callback_url")
                },
                timeout=30.0
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Runway API error: {response.text}")
            
            data = response.json()
            
            return {
                "task_id": data.get("id", task_id),
                "status": data.get("status", "pending"),
                "estimated_time": data.get("estimated_time", duration * 10)
            }
    
    async def generate_from_script(
        self,
        script: Dict[str, Any],
        duration: int = 4,
        clarity: str = "1080p",
        style: str = None
    ) -> Dict[str, Any]:
        prompt = script.get("script", str(script))
        if style:
            prompt = f"{prompt}, {style} style"
        
        return await self.generate(
            prompt=prompt,
            duration=duration,
            resolution=clarity,
            style=style
        )
    
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Runway API error: {response.text}")
            
            data = response.json()
            
            return {
                "task_id": task_id,
                "status": data.get("status", "unknown"),
                "progress": data.get("progress", 0),
                "result_url": data.get("result_url"),
                "error": data.get("error")
            }
    
    async def cancel(self, task_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tasks/{task_id}/cancel",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=30.0
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
        style: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        return await self.runway.generate(
            prompt=prompt,
            duration=duration,
            resolution=clarity,
            style=style,
            **kwargs
        )
    
    async def generate_from_script(
        self,
        script: Dict[str, Any],
        duration: int = 4,
        clarity: str = "1080p",
        style: str = None
    ) -> Dict[str, Any]:
        return await self.runway.generate_from_script(
            script=script,
            duration=duration,
            clarity=clarity,
            style=style
        )
    
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        return await self.runway.get_status(task_id)
    
    async def cancel(self, task_id: str) -> bool:
        return await self.runway.cancel(task_id)


runway_service = RunwayService()
video_generator = VideoGenerator()
