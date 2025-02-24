from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services.instructor_service import CourseService
from api.schema.instructor_schema import AssignInstructorsSchema, CourseCreateSchema, CourseResponse, InstructorResponseSchema
from config.database import get_db
from config.auth import get_current_instructor
from api.model.attendance_model import Course, Instructor, User

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



@router.get("/get_all_instructors", response_model=list[InstructorResponseSchema])
def get_instructors(
    current_user=Depends(get_current_instructor),
    db: Session = Depends(get_db)
    ):
    """Retrieve all instructors"""
    instructors = (
         db.query(Instructor.id, Instructor.instructor_id, Instructor.department, User.email)
            .join(User, Instructor.user_id == User.id)
            .all()
    )
    if not instructors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No instructors found."
        )
    return instructors

@router.get("/get_included_instructors", response_model=List[CourseResponse])
async def get_instructor_course(
    current_user= Depends(get_current_instructor),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)

):
    courses = CourseService.get_instructor_course(
        current_user=current_user.id,
        db=db,
        skip=skip,
        limit=limit
    )
    return courses