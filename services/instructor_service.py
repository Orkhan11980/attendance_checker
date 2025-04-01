from typing import List
from sqlalchemy.orm import Session, joinedload
from api.model.attendance_model import AttendanceRecord, Course, Instructor, QRSession, instructor_course
from api.schema.instructor_schema import AssignInstructorsSchema, CourseCreateSchema, CourseResponse, Credentials, UserResponse  
from api.schema.instructor_schema import CourseCreateSchema
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


class CourseService:
    @staticmethod
    def create_course(current_user: Credentials, current_user_id: int, course_data: CourseCreateSchema, db: Session):

        instructor = db.query(Instructor).filter(Instructor.user_id == current_user_id).first()
        if not instructor:
            raise HTTPException(status_code=404, detail="Instructor not found")
        
        existing_course = db.query(Course).filter(Course.crn == course_data.crn).first()
        if existing_course:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course already exists"
                )
        new_course = Course(
            crn=course_data.crn,
            course_name=course_data.course_name,
            semester=course_data.semester,
            year=course_data.year,
            created_by= current_user
        )
        instructor.courses.append(new_course)

        db.add(new_course)
        db.commit()
        db.refresh(new_course)


        return {"success": True, "course_id": new_course.id}

    @staticmethod
    def assign_instructors(current_user: Credentials, data: AssignInstructorsSchema, db: Session):
        
        if current_user != "instructor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized instructors can perform this action."
            )
        # Check if the course exists
        course = db.query(Course).filter(Course.id == data.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check if all provided instructor IDs exist
        instructors = db.query(Instructor).filter(Instructor.id.in_(data.instructor_ids)).all()
        if len(instructors) != len(data.instructor_ids):
            raise HTTPException(status_code=400, detail="Some instructors not found")

        # Add instructors to the course, avoiding duplicates
        for instructor in instructors:
            # Check if the instructor is already assigned to the course
            existing_assignment = (
                db.query(instructor_course)
                .filter(
                    instructor_course.c.instructor_id == instructor.id,
                    instructor_course.c.course_id == course.id,
                )
                .first()
            )
            if not existing_assignment:
                # Only insert if the instructor is not already assigned to the course
                db.execute(
                    instructor_course.insert().values(
                        instructor_id=instructor.id, course_id=course.id
                    )
                )

        db.commit()
        return {"success": True, "course_id": data.course_id}

    @staticmethod
    def delete_course(role: str, email: str, course_id: int, db: Session) -> dict:
        # Only authorized instructors or admins can delete courses
        if role not in ["instructor", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized instructors or admins can perform this action."
            )

        # Check if the course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Ensure the current user is the one who created the course
        if email != course.created_by:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this course")
        
        try:
            # Delete attendance records related to this course
            db.query(AttendanceRecord).filter(AttendanceRecord.course_id == course_id).delete()

            # Delete QR sessions related to this course
            db.query(QRSession).filter(QRSession.course_id == course_id).delete()

            # Delete instructor-course assignments
            db.query(instructor_course).filter(instructor_course.c.course_id == course_id).delete()

            # Finally, delete the course
            db.delete(course)
            db.commit()

            return {"success": True, "message": "Course and all associated records deleted successfully"}
        
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete course due to database constraints.")


    
    @staticmethod
    def get_instructor_course(current_user: int, db: Session, skip: int = 0, limit: int = 20,):
        
            instructor = db.query(Instructor).filter(Instructor.user_id == current_user).first()
            if not instructor:
                raise HTTPException(status_code=404, detail="Instructor not found")
            
            courses = (
                    db.query(Course)
                    .join(instructor_course)
                    .filter(instructor_course.c.instructor_id == instructor.id)
                    .options(
                        joinedload(Course.instructors).joinedload(Instructor.user)
                    )
                    .order_by(Course.created_at.desc())
                    .offset(skip)
                    .limit(limit)
                    .all()
                  )
                
            course_response = [
                 CourseResponse(
                    id = course.id,
                    crn=course.crn,
                    course_name=course.course_name,
                    semester=course.semester,
                    year=course.year,
                    created_at=course.created_at,
                    created_by=course.created_by,
                    instructors=[
                        UserResponse(
                            first_name=instructor.user.first_name,
                            last_name=instructor.user.last_name
                        )
                        for instructor in course.instructors
                        if instructor.user 
            ]

                 )
                 for course in courses
            ]
            return course_response