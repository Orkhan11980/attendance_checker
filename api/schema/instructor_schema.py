from pydantic import BaseModel
from typing import List, Optional

class CourseCreateSchema(BaseModel):
    crn: str
    course_name: str
    semester: str
    year: int



class Credentials:
    email: str


class AssignInstructorsSchema(BaseModel):
    course_id: int
    instructor_ids: List[int]



class InstructorResponseSchema(BaseModel):
    id: int
    instructor_id: str
    department: str
    email: str
    first_name: str
    last_name: str


#
from datetime import datetime


class UserResponse(BaseModel):
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: int
    crn: str
    course_name: str
    semester: str
    year: int
    created_at: datetime
    created_by: str
    instructors: List[UserResponse] = []

    class Config:
        from_attributes = True


class StudentResponse(BaseModel):
    id: int
    user_id: int
    student_id: str
    phone_id: str
    phone_model: str
    registered_at: datetime
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True