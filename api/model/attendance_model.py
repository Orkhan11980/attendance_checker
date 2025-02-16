from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from api.model.base_model import Base

# Association table for instructor-course many-to-many relationship
instructor_course = Table(
    'instructor_course',
    Base.metadata,
    Column('instructor_id', Integer, ForeignKey('instructors.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed password
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # 'student' or 'instructor'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    student_id = Column(String(50), unique=True, nullable=False)
    phone_id = Column(String(100), unique=True, nullable=False)
    phone_model = Column(String(100), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

class Instructor(Base):
    __tablename__ = 'instructors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    instructor_id = Column(String(50), unique=True, nullable=False)
    department = Column(String(100), nullable=False)

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    crn = Column(String(20), unique=True, nullable=False)
    course_name = Column(String(200), nullable=False)
    semester = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class QRSession(Base):
    __tablename__ = 'qr_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    instructor_id = Column(Integer, ForeignKey('instructors.id'), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    qr_code_data = Column(String(500), nullable=False)

class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    qr_session_id = Column(Integer, ForeignKey('qr_sessions.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    phone_id = Column(String(100), nullable=False)  # For verification
    phone_model = Column(String(100), nullable=False)
