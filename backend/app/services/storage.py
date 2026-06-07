import os
import shutil
import uuid
from abc import ABC, abstractmethod
from fastapi import UploadFile

class StorageProvider(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, user_id: str) -> str:
        pass

    @abstractmethod
    def read(self, storage_path: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, storage_path: str) -> bool:
        pass


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save(self, file: UploadFile, user_id: str) -> str:
        user_dir = os.path.join(self.base_dir, f"user_{user_id}")
        os.makedirs(user_dir, exist_ok=True)
        
        # Secure filename to prevent path traversal
        filename = os.path.basename(file.filename)
        # Prefix with uuid to prevent overwriting
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Forward slashes for consistency across OS if stored in DB
        storage_path = f"{self.base_dir}/user_{user_id}/{unique_filename}"
        
        # Local physical path
        physical_path = os.path.join(user_dir, unique_filename)
        
        with open(physical_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return storage_path

    def read(self, storage_path: str) -> bytes:
        # Normalize path for local OS
        physical_path = os.path.normpath(storage_path)
        with open(physical_path, "rb") as f:
            return f.read()

    def delete(self, storage_path: str) -> bool:
        physical_path = os.path.normpath(storage_path)
        if os.path.exists(physical_path):
            os.remove(physical_path)
            return True
        return False


def get_storage_provider() -> StorageProvider:
    """Factory selecting the storage backend from config.

    Add new backends (e.g. S3StorageProvider) here — call sites depend only on
    the StorageProvider interface, so swapping is a one-line change.
    """
    from app.core.config import settings
    backend = (settings.STORAGE_BACKEND or "local").lower()
    if backend == "local":
        return LocalStorageProvider(base_dir=settings.STORAGE_LOCAL_DIR)
    raise ValueError(f"Unsupported STORAGE_BACKEND: {backend!r}")
