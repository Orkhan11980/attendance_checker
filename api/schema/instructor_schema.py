from pydantic import BaseModel
from typing import List, Optional

class CourseCreateSchema(BaseModel):
    crn: str
    course_name: str
    semester: str
    year: int

class CourseResponseSchema(BaseModel):
    id: int
    crn: str
    course_name: str
    semester: str
    year: int
    instructors: List[int] 

    class Config:
        orm_mode = True

class InstructorAssignSchema(BaseModel):
    instructor_id: int

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

