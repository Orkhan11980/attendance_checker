from pydantic import BaseModel
from datetime import datetime

class AttendanceBase(BaseModel):
    student_id: str
    student_name: str
    student_surname: str
    student_email: str

class AttendanceCreate(AttendanceBase):
    platform: str
    model: str
    device_id: str

class AttendanceResponse(AttendanceBase):
    timestamp: datetime

    class Config:
        from_attributes = True
