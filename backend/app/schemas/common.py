from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class BaseResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000)
    )


class ErrorResponse(BaseModel):
    code: int
    message: str
    errors: Optional[list] = None
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp() * 1000)
    )


class PaginationData(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseResponse):
    data: PaginationData
