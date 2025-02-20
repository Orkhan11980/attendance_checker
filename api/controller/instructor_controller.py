from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.instructor_service import CourseService
from api.schema.instructor_schema import AssignInstructorsSchema, CourseCreateSchema, InstructorAssignSchema, CourseResponseSchema
from config.database import get_db
from config.auth import get_current_instructor
from api.model.attendance_model import Course

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("/")
async def create_course(
    course_data: CourseCreateSchema,
    current_user=Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """Instructor creates a course."""
    course = CourseService.create_course(current_user.email, course_data, db)
    return course


@router.post("/assign-instructors")
async def assign_instructors(
    data: AssignInstructorsSchema,
    current_user=Depends(get_current_instructor),  # Only instructors can assign
    db: Session = Depends(get_db)
):
    """Assign instructors to a course."""
    return CourseService.assign_instructors(current_user.role, data, db)


@router.delete("/delete/{course_id}")
async def delete_course(
    course_id: int,
    current_user=Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """Instructor creates a course."""
    course = CourseService.delete_course(current_user.role, course_id, db)
    return course

