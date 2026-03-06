from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class BaseAIService(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def cancel(self, task_id: str) -> bool:
        pass
