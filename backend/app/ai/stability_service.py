from __future__ import annotations

import time
from typing import Any, Dict

import httpx

from app.ai.base import BaseAIService
from app.services.ai_provider_config_service import AIProviderConfigService


class StabilityAIService(BaseAIService):
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0,
        seed: int = 0,
        style_preset: str | None = None,
        **kwargs,
    ) -> Dict[str, Any]:
        runtime = AIProviderConfigService.get_runtime_config().get("stability", {})
        api_key = runtime.get("api_key", "")
        base_url = (runtime.get("api_base") or "https://api.stability.ai/v1").rstrip("/")
        engine = runtime.get("engine") or "stable-diffusion-xl-1024-v1-0"

        if not api_key:
            raise Exception("Stability API key is not configured")

        text_prompts = [{"text": prompt, "weight": 1.0}]
        if negative_prompt:
            text_prompts.append({"text": negative_prompt, "weight": -1.0})

        payload: Dict[str, Any] = {
            "text_prompts": text_prompts,
            "cfg_scale": cfg_scale,
            "height": height,
            "width": width,
            "steps": steps,
            "seed": seed if seed else int(time.time()),
        }
        if style_preset:
            payload["style_preset"] = style_preset

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/generation/{engine}/text-to-image",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120.0,
            )

            if response.status_code != 200:
                raise Exception(f"Stability API error: {response.text}")

            data = response.json()
            return {
                "images": [
                    {
                        "base64": image.get("base64"),
                        "seed": image.get("seed"),
                        "finish_reason": image.get("finishReason"),
                    }
                    for image in data.get("artifacts", [])
                ],
                "seed": data.get("seed", seed),
            }

    async def generate_from_script(
        self,
        script: Dict[str, Any],
        clarity: str = "1080p",
        style: str | None = None,
        count: int = 1,
    ) -> Dict[str, Any]:
        # Stability接口更稳定的分辨率映射。
        resolutions = {
            "720p": (1280, 768),
            "1080p": (1536, 896),
            "4k": (2048, 1152),
        }
        width, height = resolutions.get(clarity, (1536, 896))

        prompt = script.get("script", str(script))
        if style:
            prompt = f"{prompt}, {style} style"

        images = []
        for _ in range(max(1, count)):
            result = await self.generate(
                prompt=prompt,
                width=width,
                height=height,
                style_preset=style,
            )
            images.extend(result.get("images", []))

        return {
            "images": images,
            "count": len(images),
            "clarity": clarity,
            "style": style,
        }

    async def image_to_image(
        self,
        init_image: str,
        prompt: str,
        image_strength: float = 0.35,
        **kwargs,
    ) -> Dict[str, Any]:
        runtime = AIProviderConfigService.get_runtime_config().get("stability", {})
        api_key = runtime.get("api_key", "")
        base_url = (runtime.get("api_base") or "https://api.stability.ai/v1").rstrip("/")
        engine = runtime.get("engine") or "stable-diffusion-xl-1024-v1-0"

        if not api_key:
            raise Exception("Stability API key is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/generation/{engine}/image-to-image",
                headers={"Authorization": f"Bearer {api_key}"},
                data={
                    "text_prompts[0][text]": prompt,
                    "init_image": init_image,
                    "image_strength": image_strength,
                    **kwargs,
                },
                timeout=120.0,
            )

            if response.status_code != 200:
                raise Exception(f"Stability API error: {response.text}")

            data = response.json()
            return {
                "images": [
                    {"base64": image.get("base64"), "seed": image.get("seed")}
                    for image in data.get("artifacts", [])
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
        style: str | None = None,
        count: int = 1,
        **kwargs,
    ) -> Dict[str, Any]:
        result = await self.stability.generate_from_script(
            script={"script": prompt},
            clarity=clarity,
            style=style,
            count=count,
        )
        return {"images": result.get("images", [])}

    async def generate_from_script(
        self,
        script: Dict[str, Any],
        clarity: str = "1080p",
        style: str | None = None,
        count: int = 1,
    ) -> Dict[str, Any]:
        return await self.stability.generate_from_script(
            script=script,
            clarity=clarity,
            style=style,
            count=count,
        )

    async def generate_with_reference(self, reference_image: str, prompt: str, **kwargs) -> Dict[str, Any]:
        return await self.stability.image_to_image(
            init_image=reference_image,
            prompt=prompt,
            **kwargs,
        )


stability_service = StabilityAIService()
image_generator = ImageGenerator()

