from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)  # Maps to full_name
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user: dict # Contains id, name, email
    token: str

class LearnerProfileDTO(BaseModel):
    confidence_level: Optional[int] = None
    experience_level: Optional[str] = None
    preferred_examples: Optional[str] = None
    learning_velocity: Optional[str] = None
    preferred_study_minutes: Optional[int] = None

class UserDTO(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    profile: Optional[LearnerProfileDTO] = None
