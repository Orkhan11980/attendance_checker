from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.instructor_service import CourseService
from api.schema.instructor_schema import  InstructorPersonalDataSchema
from config.database import get_db
from config.auth import get_current_instructor



router = APIRouter(prefix="/get_personal_data", tags=["Personal Data"])


@router.get("/instructor", response_model=InstructorPersonalDataSchema)
def get_personal_data(
    current_user=Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    return CourseService.get_personal_data(current_user, db)