from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScriptCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1, description="Script content")
    keywords: Optional[str] = Field(None, min_length=1, description="Keywords for script generation")
    output_type: str = Field(..., description="image_set/single_image/video")
    parameters: Optional[dict] = None

    @field_validator("output_type")
    @classmethod
    def validate_output_type(cls, value: str):
        if value not in {"image_set", "single_image", "video"}:
            raise ValueError("Invalid output_type")
        return value

    @model_validator(mode="after")
    def validate_content_or_keywords(self):
        if not self.content and not self.keywords:
            raise ValueError("Either content or keywords must be provided")
        return self


class ScriptUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1, description="Script content")
    parameters: Optional[dict] = None


class ScriptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: Optional[str]
    content: str
    output_type: str
    parameters: Optional[dict]
    status: int
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    task_type: str = Field(..., description="script/image/video/ad")
    parameters: dict = Field(..., description="Task parameters")

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, value: str):
        if value not in {"script", "image", "video", "ad"}:
            raise ValueError("Invalid task_type")
        return value

    @field_validator("parameters")
    @classmethod
    def validate_parameters(cls, value: dict, info):
        task_type = info.data.get("task_type")

        if task_type == "script":
            keywords = value.get("keywords")
            if not isinstance(keywords, str) or not keywords.strip():
                raise ValueError("keywords is required for script tasks")
        elif task_type in {"image", "video"}:
            prompt = value.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("prompt is required for image/video tasks")
        elif task_type == "ad":
            creative_plan = value.get("creative_plan")
            if not isinstance(creative_plan, str) or not creative_plan.strip():
                raise ValueError("creative_plan is required for ad tasks")

        return value


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    task_no: str
    task_type: str
    status: int
    progress: int
    parameters: Optional[dict]
    result_url: Optional[str]
    error_message: Optional[str]
    cost_amount: int
    completed_at: Optional[datetime]
    created_at: datetime


class WorkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    task_id: Optional[int]
    work_type: str
    title: Optional[str]
    file_url: str
    thumbnail_url: Optional[str]
    parameters: Optional[dict]
    is_public: int
    quality_score: Optional[int]
    created_at: datetime
