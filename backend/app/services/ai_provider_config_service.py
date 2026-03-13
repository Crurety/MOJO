from __future__ import annotations

import time
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.exceptions import BadRequestException
from app.services.system_config_service import SystemConfigService


class AIProviderConfigService:
    PROVIDERS = ("openai", "deepseek", "stability", "runway")

    PROVIDER_FIELDS = {
        "openai": (
            "api_key",
            "api_base",
            "model",
            "wire_api",
            "reasoning_effort",
            "disable_response_storage",
            "context_window",
        ),
        "deepseek": (
            "api_key",
            "api_base",
            "model",
        ),
        "stability": ("api_key", "api_base", "engine"),
        "runway": ("api_key", "api_base"),
    }

    CONFIG_KEY_MAP = {
        "openai": {
            "api_key": "openai_api_key",
            "api_base": "openai_api_base",
            "model": "openai_model",
            "wire_api": "openai_wire_api",
            "reasoning_effort": "openai_reasoning_effort",
            "disable_response_storage": "openai_disable_response_storage",
            "context_window": "openai_context_window",
        },
        "deepseek": {
            "api_key": "deepseek_api_key",
            "api_base": "deepseek_api_base",
            "model": "deepseek_model",
        },
        "stability": {
            "api_key": "stability_api_key",
            "api_base": "stability_api_base",
            "engine": "stability_engine",
        },
        "runway": {
            "api_key": "runway_api_key",
            "api_base": "runway_api_base",
        },
    }

    ENV_FALLBACKS = {
        "openai_api_key": settings.OPENAI_API_KEY or "",
        "openai_api_base": settings.OPENAI_API_BASE or "",
        "openai_model": settings.OPENAI_MODEL or "gpt-4",
        "openai_wire_api": settings.OPENAI_API_WIRE or "",
        "openai_reasoning_effort": settings.OPENAI_REASONING_EFFORT or "",
        "openai_disable_response_storage": str(settings.OPENAI_DISABLE_RESPONSE_STORAGE).lower(),
        "openai_context_window": str(settings.OPENAI_CONTEXT_WINDOW or ""),
        "deepseek_api_key": settings.DEEPSEEK_API_KEY or "",
        "deepseek_api_base": settings.DEEPSEEK_API_BASE or "https://api.deepseek.com",
        "deepseek_model": settings.DEEPSEEK_MODEL or "deepseek-chat",
        "stability_api_key": settings.STABILITY_API_KEY or "",
        "stability_api_base": settings.STABILITY_API_BASE or "https://api.stability.ai/v1",
        "stability_engine": settings.STABILITY_ENGINE or "stable-diffusion-xl-1024-v1-0",
        "runway_api_key": settings.RUNWAY_API_KEY or "",
        "runway_api_base": settings.RUNWAY_API_BASE or "https://api.runwayml.com/v1",
    }

    FIELD_DESCRIPTIONS = {
        "openai_api_key": "OpenAI API key",
        "openai_api_base": "OpenAI API base URL",
        "openai_model": "OpenAI model name",
        "openai_wire_api": "OpenAI API wire mode",
        "openai_reasoning_effort": "OpenAI reasoning effort",
        "openai_disable_response_storage": "OpenAI response storage disabled",
        "openai_context_window": "OpenAI model context window",
        "deepseek_api_key": "DeepSeek API key",
        "deepseek_api_base": "DeepSeek API base URL",
        "deepseek_model": "DeepSeek model name",
        "stability_api_key": "Stability API key",
        "stability_api_base": "Stability API base URL",
        "stability_engine": "Stability engine",
        "runway_api_key": "Runway API key",
        "runway_api_base": "Runway API base URL",
    }

    _runtime_cache: Optional[Dict[str, Dict[str, str]]] = None
    _runtime_cache_at: float = 0.0
    _runtime_cache_ttl_seconds: int = 15

    def __init__(self, db: Session):
        self.db = db
        self.system_config_service = SystemConfigService(db)

    @classmethod
    def _all_config_keys(cls) -> list[str]:
        keys: list[str] = []
        for provider in cls.PROVIDERS:
            for field in cls.PROVIDER_FIELDS[provider]:
                keys.append(cls.CONFIG_KEY_MAP[provider][field])
        return keys

    @staticmethod
    def _mask_secret(value: str) -> str:
        if not value:
            return ""
        if len(value) <= 8:
            return "*" * len(value)
        return f"{value[:4]}***{value[-4:]}"

    def _get_raw_config_values(self) -> Dict[str, str]:
        values = self.system_config_service.get_values(self._all_config_keys())
        merged = dict(self.ENV_FALLBACKS)
        merged.update({k: v for k, v in values.items() if v is not None})
        return merged

    def get_providers_for_admin(self) -> Dict[str, Dict[str, str | bool]]:
        raw_values = self._get_raw_config_values()
        data: Dict[str, Dict[str, str | bool]] = {}

        for provider in self.PROVIDERS:
            provider_data: Dict[str, str | bool] = {}
            key_value = ""
            for field in self.PROVIDER_FIELDS[provider]:
                config_key = self.CONFIG_KEY_MAP[provider][field]
                value = (raw_values.get(config_key) or "").strip()
                if field == "api_key":
                    key_value = value
                    provider_data[field] = self._mask_secret(value)
                else:
                    provider_data[field] = value

            provider_data["enabled"] = bool(key_value)
            data[provider] = provider_data

        return data

    def update_provider(self, provider: str, payload: Dict[str, str | None]) -> None:
        provider = provider.lower().strip()
        if provider not in self.PROVIDERS:
            raise BadRequestException(detail=f"Unsupported provider: {provider}")
        if not isinstance(payload, dict):
            raise BadRequestException(detail="Invalid payload")

        allowed_fields = set(self.PROVIDER_FIELDS[provider])
        unknown_fields = [key for key in payload.keys() if key not in allowed_fields]
        if unknown_fields:
            raise BadRequestException(detail=f"Unknown fields: {', '.join(unknown_fields)}")

        values_to_save: Dict[str, str] = {}
        descriptions: Dict[str, str] = {}

        for field, raw_value in payload.items():
            if raw_value is None:
                continue

            value = str(raw_value).strip()
            config_key = self.CONFIG_KEY_MAP[provider][field]

            values_to_save[config_key] = value
            descriptions[config_key] = self.FIELD_DESCRIPTIONS.get(config_key, "AI provider config")

        if values_to_save:
            self.system_config_service.set_values(values_to_save, descriptions)
            self.invalidate_runtime_cache()

    @classmethod
    def invalidate_runtime_cache(cls) -> None:
        cls._runtime_cache = None
        cls._runtime_cache_at = 0.0

    @classmethod
    def get_runtime_config(cls, force_refresh: bool = False) -> Dict[str, Dict[str, str]]:
        now = time.time()
        cache_valid = (
            cls._runtime_cache is not None
            and (now - cls._runtime_cache_at) < cls._runtime_cache_ttl_seconds
        )
        if not force_refresh and cache_valid:
            return cls._runtime_cache or {}

        raw_values: Dict[str, str]
        db = SessionLocal()
        try:
            service = cls(db)
            raw_values = service._get_raw_config_values()
        except Exception:
            # Keep runtime services available when DB is temporarily unavailable.
            raw_values = dict(cls.ENV_FALLBACKS)
        finally:
            db.close()

        runtime: Dict[str, Dict[str, str]] = {}
        for provider in cls.PROVIDERS:
            runtime[provider] = {}
            for field in cls.PROVIDER_FIELDS[provider]:
                key = cls.CONFIG_KEY_MAP[provider][field]
                runtime[provider][field] = (raw_values.get(key) or "").strip()

        cls._runtime_cache = runtime
        cls._runtime_cache_at = now
        return runtime
