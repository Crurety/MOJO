from typing import Dict, Any, Optional, List
from app.ai.base import BaseAIService
from app.core.config import settings
import httpx
import uuid
import time


class StabilityAIService(BaseAIService):
    def __init__(self):
        self.api_key = settings.STABILITY_API_KEY
        self.base_url = settings.STABILITY_API_BASE or "https://api.stability.ai/v1"
        self.engine = settings.STABILITY_ENGINE or "stable-diffusion-xl-1024-v1-0"
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0,
        seed: int = 0,
        style_preset: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generation/{self.engine}/text-to-image",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text_prompts": [
                        {"text": prompt, "weight": 1.0},
                        {"text": negative_prompt, "weight": -1.0} if negative_prompt else None
                    ],
                    "cfg_scale": cfg_scale,
                    "height": height,
                    "width": width,
                    "steps": steps,
                    "seed": seed if seed else int(time.time()),
                    "style_preset": style_preset
                },
                timeout=120.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Stability AI API error: {response.text}")
            
            data = response.json()
            
            return {
                "images": [
                    {
                        "base64": img.get("base64"),
                        "seed": img.get("seed"),
                        "finish_reason": img.get("finishReason")
                    }
                    for img in data.get("artifacts", [])
                ],
                "seed": data.get("seed", seed)
            }
    
    async def generate_from_script(
        self,
        script: Dict[str, Any],
        clarity: str = "1080p",
        style: str = None,
        count: int = 1
    ) -> Dict[str, Any]:
        resolutions = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "4k": (3840, 2160)
        }
        
        width, height = resolutions.get(clarity, (1920, 1080))
        
        prompt = script.get("script", str(script))
        if style:
            prompt = f"{prompt}, {style} style"
        
        results = []
        for i in range(count):
            result = await self.generate(
                prompt=prompt,
                width=width,
                height=height,
                style_preset=style
            )
            results.append(result)
        
        return {
            "images": results,
            "count": count,
            "clarity": clarity,
            "style": style
        }
    
    async def image_to_image(
        self,
        init_image: str,
        prompt: str,
        image_strength: float = 0.35,
        **kwargs
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generation/{self.engine}/image-to-image",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                },
                data={
                    "text_prompts[0][text]": prompt,
                    "init_image": init_image,
                    "image_strength": image_strength,
                    **kwargs
                },
                timeout=120.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Stability AI API error: {response.text}")
            
            data = response.json()
            
            return {
                "images": [
                    {
                        "base64": img.get("base64"),
                        "seed": img.get("seed")
                    }
                    for img in data.get("artifacts", [])
                ]
            }
    
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        return {"status": "completed", "task_id": task_id}
    
    async def cancel(self, task_id: str) -> bool:
        return True


class ImageGenerator:
    def __init__(self):
        self.stability = StabilityAIService()
    
    async def generate_single(
        self,
        prompt: str,
        clarity: str = "1080p",
        style: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        return await self.stability.generate(
            prompt=prompt,
            style_preset=style,
            **kwargs
        )
    
    async def generate_from_script(
        self,
        script: Dict[str, Any],
        clarity: str = "1080p",
        style: str = None,
        count: int = 1
    ) -> Dict[str, Any]:
        return await self.stability.generate_from_script(
            script=script,
            clarity=clarity,
            style=style,
            count=count
        )
    
    async def generate_with_reference(
        self,
        reference_image: str,
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        return await self.stability.image_to_image(
            init_image=reference_image,
            prompt=prompt,
            **kwargs
        )


stability_service = StabilityAIService()
image_generator = ImageGenerator()
