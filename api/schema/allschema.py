# schema/auth_schema.py
from pydantic import BaseModel
from typing import Literal, Optional, List
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: Literal['admin', 'instructor', 'student']

class UserCreate(UserBase):
    password: str

class InstructorRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    instructor_id: str
    department: str

class StudentRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    student_id: str
    phone_id: str
    phone_model: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[UUID] = None