
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QRSessionCreateSchema(BaseModel):
    course_id: int
    expires_in: Optional[int] = 1  # Default expiration time in minutes

class QRScanSchema(BaseModel):
    qr_code_data: str
    phone_id: str
    phone_model: str

class QRSessionResponseSchema(BaseModel):
    id: int
    course_id: int
    instructor_id: int
    generated_at: datetime
    expires_at: datetime
    is_active: bool
    qr_code_data: str

class QRScanResponseSchema(BaseModel):
    success: bool
    message: str
