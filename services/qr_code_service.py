from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from api.model.attendance_model import Course, Instructor, QRSession, AttendanceRecord, Student, User, instructor_course
from api.schema.qr_schema import QRSessionCreateSchema, QRScanSchema

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
            expires_at = datetime.utcnow() + timedelta(minutes=data.expires_in)
            qr_code_data = str(uuid.uuid4())  # Unique QR code data

            qr_session = QRSession(
                course_id=data.course_id,
                instructor_id=instructor.id,
                generated_at=datetime.utcnow(),
                expires_at=expires_at,
                is_active=True,
                qr_code_data=qr_code_data
            )
            db.add(qr_session)
            db.commit()
            db.refresh(qr_session)
            
            return {"qr_code_data": qr_code_data, "expires_at": expires_at}


    @staticmethod
    def scan_qr(current_user: int , qr_data: QRScanSchema, db: Session):
        qr_session = db.query(QRSession).filter(QRSession.qr_code_data == qr_data.qr_code_data).first()
        if not qr_session:
            raise HTTPException(status_code=400, detail="Invalid QR code")
        
        if qr_session.expires_at < datetime.utcnow() or not qr_session.is_active:
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
            timestamp=datetime.utcnow(),
            phone_id=qr_data.phone_id,
            phone_model=qr_data.phone_model
        )
        db.add(attendance)
        db.commit()
        return {"success": True, "message": "Attendance recorded"}
