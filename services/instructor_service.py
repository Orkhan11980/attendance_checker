from typing import List
from sqlalchemy.orm import Session
from api.model.attendance_model import Course, Instructor, instructor_course
from api.schema.instructor_schema import AssignInstructorsSchema, CourseCreateSchema,CourseResponseSchema, Credentials,InstructorAssignSchema  
from api.schema.instructor_schema import CourseCreateSchema
from fastapi import HTTPException, status


class CourseService:
    @staticmethod
    def create_course(current_user: Credentials, course_data: CourseCreateSchema, db: Session):

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


    def delete_course(current_user: Credentials, course_id: int, db: Session):
            # Check if the current user is authorized (e.g., an instructor or admin)
            if current_user not in ["instructor", "admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only authorized instructors or admins can perform this action."
                )

            # Check if the course exists
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")

            # Delete all associated rows in the instructor_course table
            db.query(instructor_course).filter(instructor_course.c.course_id == course_id).delete()

            # Delete the course
            db.delete(course)
            db.commit()

            return {"success": True, "message": "Course and associated instructor assignments deleted successfully"}