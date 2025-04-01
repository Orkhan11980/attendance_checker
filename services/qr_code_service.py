from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from api.model.attendance_model import Course, Instructor, QRSession, AttendanceRecord, Student, User, get_baku_time, instructor_course
from api.schema.qr_schema import QRSessionCreateSchema, QRScanSchema, StudentResponseSchema
from typing import List
from api.model.attendance_model import baku_tz
class QRService:
    
  class QRService:
    
    @staticmethod
    def generate_qr_session(data: QRSessionCreateSchema, user_id: int, db: Session):
            # Check if the course exists
            course = db.query(Course).filter(Course.id == data.course_id).first()
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course with ID {data.course_id} does not exist."
                )

            instructor = db.query(Instructor).filter(Instructor.user_id == user_id).first()
            if not instructor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Instructor with user ID {user_id} not found."
                )
            # Check if the instructor is enrolled in the course
            enrollment = db.query(instructor_course).filter(
                instructor_course.c.instructor_id == instructor.id,
                instructor_course.c.course_id == data.course_id
            ).first()
            if not enrollment:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Instructor with ID {instructor.id} is not enrolled in course with ID {data.course_id}."
                )

            # Generate QR session
            current_time = get_baku_time()
            expires_at = current_time + timedelta(seconds=data.expires_in)
            qr_code_data = str(uuid.uuid4())  # Unique QR code data

            qr_session = QRSession(
                course_id=data.course_id,
                instructor_id=instructor.id,
                generated_at=current_time,
                expires_at=expires_at,
                is_active=True,
                qr_code_data=qr_code_data
            )
            db.add(qr_session)
            db.commit()
            db.refresh(qr_session)
            
            return {"qr_code_data": qr_code_data, "expires_at": expires_at}


    @staticmethod
    def scan_qr(current_user: int, qr_data: QRScanSchema, db: Session):
        qr_session = db.query(QRSession).filter(QRSession.qr_code_data == qr_data.qr_code_data).first()
        if not qr_session:
            raise HTTPException(status_code=400, detail="Invalid QR code")
        
        current_time = get_baku_time()
        if qr_session.expires_at < current_time or not qr_session.is_active:
            raise HTTPException(status_code=400, detail="QR code expired")
        
        student = db.query(Student).filter(Student.user_id == current_user).first()        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        if student.phone_id != qr_data.phone_id or student.phone_model != qr_data.phone_model:
            raise HTTPException(status_code=400, detail="Device mismatch")
        
        existing_attendance = db.query(AttendanceRecord).filter(
            AttendanceRecord.qr_session_id == qr_session.id,
            AttendanceRecord.student_id == student.id
        ).first()
        
        if existing_attendance:
            raise HTTPException(status_code=400, detail="Already scanned for this session")
        
        attendance = AttendanceRecord(
            qr_session_id=qr_session.id,
            student_id=student.id,
            course_id=qr_session.course_id,
            timestamp=current_time,
            phone_id=qr_data.phone_id,
            phone_model=qr_data.phone_model
        )
        db.add(attendance)
        db.commit()
        return {"success": True, "message": "Attendance recorded"}
    
    

    @staticmethod
    def get_scanned_students(course_id: int, db: Session) -> List[StudentResponseSchema]:
            records = db.query(AttendanceRecord).filter(AttendanceRecord.course_id == course_id).all()

            if not records:
                raise HTTPException(status_code=404, detail="No attendance records found for this session")

            student_ids = [rec.student_id for rec in records]

            # Join with User to fetch name and surname
            students = (
                db.query(Student, User)
                .join(User, Student.user_id == User.id)
                .filter(Student.id.in_(student_ids))
                .all()
            )

            return [
                StudentResponseSchema(
                    id=student.Student.id,
                    student_id=student.Student.student_id,
                    first_name=student.User.first_name,
                    last_name=student.User.last_name,
                    phone_id=student.Student.phone_id,
                    scanned_at=next((rec.timestamp for rec in records if rec.student_id == student.Student.id), None),
                )
                for student in students
            ]