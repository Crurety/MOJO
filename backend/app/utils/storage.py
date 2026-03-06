import os
import uuid
from datetime import datetime
from typing import Optional
import aiofiles
from app.core.config import settings


class StorageService:
    def __init__(self):
        self.upload_dir = "uploads"
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def _get_date_path(self) -> str:
        now = datetime.now()
        return f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    async def save_file(
        self,
        file_content: bytes,
        file_extension: str,
        sub_dir: str = ""
    ) -> str:
        date_path = self._get_date_path()
        file_name = f"{uuid.uuid4().hex}{file_extension}"
        
        if sub_dir:
            relative_path = f"{sub_dir}/{date_path}/{file_name}"
        else:
            relative_path = f"{date_path}/{file_name}"
        
        full_path = os.path.join(self.upload_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(file_content)
        
        return relative_path
    
    def get_file_url(self, relative_path: str) -> str:
        if settings.OSS_BUCKET_NAME:
            return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{relative_path}"
        return f"/uploads/{relative_path}"
    
    def delete_file(self, relative_path: str) -> bool:
        full_path = os.path.join(self.upload_dir, relative_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    
    def get_file_size(self, relative_path: str) -> Optional[int]:
        full_path = os.path.join(self.upload_dir, relative_path)
        if os.path.exists(full_path):
            return os.path.getsize(full_path)
        return None


storage_service = StorageService()
