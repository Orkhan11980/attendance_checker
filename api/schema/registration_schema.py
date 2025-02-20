from pydantic import BaseModel
from typing import Optional

# regist
class UserRegisterSchema(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: str  

class StudentRegisterSchema(UserRegisterSchema):
    student_id: str
    phone_id: str
    phone_model: str

class InstructorRegisterSchema(UserRegisterSchema):
    instructor_id: str
    department: str

class UserResponseSchema(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str

    class Config:
        from_attributes = True


# auth/login
from fastapi import Form

class LoginSchema(BaseModel):
    email: str
    password: str

    @classmethod
    def as_form(cls, email: str = Form(...), password: str = Form(...)):
        return cls(email=email, password=password)


class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
