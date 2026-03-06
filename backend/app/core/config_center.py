"""配置中心服务"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.logging import logger


class ConfigCenter:
    """配置中心"""

    def __init__(self):
        self._configs: Dict[str, Any] = {}
        self._config_file = Path("config/app_config.json")
        self._load_configs()

    def _load_configs(self):
        """加载配置"""
        try:
            if self._config_file.exists():
                with open(self._config_file, "r", encoding="utf-8") as f:
                    self._configs = json.load(f)
                logger.info("配置加载成功")
            else:
                logger.warning("配置文件不存在，使用默认配置")
                self._init_default_configs()
        except Exception as e:
            logger.error(f"配置加载失败: {str(e)}")
            self._init_default_configs()

    def _init_default_configs(self):
        """初始化默认配置"""
        self._configs = {
            "features": {
                "new_user_reward": True,
                "daily_sign_in": True,
                "invite_reward": True,
                "quality_content_reward": True,
                "ab_test": False,
            },
            "limits": {
                "max_upload_size": 10 * 1024 * 1024,  # 10MB
                "max_tasks_per_day": 100,
                "max_works_per_user": 1000,
            },
            "rewards": {
                "register_points": 100,
                "daily_sign_in_points": 10,
                "invite_points": 50,
                "share_points": 5,
            },
            "business": {
                "work_retention_days": 15,
                "task_retention_days": 30,
                "coupon_validity_days": 30,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置

        Args:
            key: 配置键，支持点号分隔的路径，如 "features.new_user_reward"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._configs

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """设置配置

        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split(".")
        config = self._configs

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        self._save_configs()

    def _save_configs(self):
        """保存配置"""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._configs, f, indent=2, ensure_ascii=False)
            logger.info("配置保存成功")
        except Exception as e:
            logger.error(f"配置保存失败: {str(e)}")

    def reload(self):
        """重新加载配置"""
        self._load_configs()

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._configs.copy()

    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用

        Args:
            feature: 功能名称

        Returns:
            是否启用
        """
        return self.get(f"features.{feature}", False)


# 全局配置中心实例
config_center = ConfigCenter()
