from config.database import get_db
from api.model.attendance_model import Instructor, Student, User
from api.schema.allschema import InstructorRegister, StudentRegister, Token, UserResponse
from services.auth_service import ACCESS_TOKEN_EXPIRE_MINUTES, AuthService
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List


# auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not AuthService.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register/instructor", response_model=UserResponse)
async def register_instructor(
    instructor_data: InstructorRegister,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    if db.query(User).filter(User.email == instructor_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if instructor_id already exists
    if db.query(Instructor).filter(Instructor.instructor_id == instructor_data.instructor_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instructor ID already exists"
        )
    
    # Create transaction to ensure both user and instructor are created
    try:
        # Create user
        hashed_password = AuthService.get_password_hash(instructor_data.password)
        db_user = User(
            email=instructor_data.email,
            password=hashed_password,
            first_name=instructor_data.first_name,
            last_name=instructor_data.last_name,
            role='instructor'
        )
        db.add(db_user)
        db.flush()  # Flush to get the user_id
        
        # Create instructor profile
        db_instructor = Instructor(
            user_id=db_user.id,
            instructor_id=instructor_data.instructor_id,
            department=instructor_data.department
        )
        db.add(db_instructor)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/register/student", response_model=UserResponse)
async def register_student(
    student_data: StudentRegister,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    if db.query(User).filter(User.email == student_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if student_id or phone_id already exists
    if db.query(Student).filter(
        (Student.student_id == student_data.student_id) |
        (Student.phone_id == student_data.phone_id)
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID or Phone ID already exists"
        )
    
    # Create transaction to ensure both user and student are created
    try:
        # Create user
        hashed_password = AuthService.get_password_hash(student_data.password)
        db_user = User(
            email=student_data.email,
            password=hashed_password,
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            role='student'
        )
        db.add(db_user)
        db.flush()  # Flush to get the user_id
        
        # Create student profile
        db_student = Student(
            user_id=db_user.id,
            student_id=student_data.student_id,
            phone_id=student_data.phone_id,
            phone_model=student_data.phone_model
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )