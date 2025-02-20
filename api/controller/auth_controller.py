from datetime import timedelta
import os
from config.database import get_db
from services.auth_service import AuthService
from services.registration_service import RegisterService
from sqlalchemy.orm import Session
from api.schema.registration_schema import LoginSchema, StudentRegisterSchema, InstructorRegisterSchema, TokenSchema, UserResponseSchema
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv



router = APIRouter(prefix="/auth", tags=["Authentication"])

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


@router.post("/register/student", response_model=UserResponseSchema)
def register_student(data: StudentRegisterSchema, db: Session = Depends(get_db)):
    user = RegisterService.register_student(data, db)
    return user


@router.post("/register/instructor", response_model=UserResponseSchema)
def register_instructor(data: InstructorRegisterSchema, db: Session = Depends(get_db)):
    user = RegisterService.register_instructor(data, db)
    return user


@router.post("/token", response_model=TokenSchema)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),  # Accept form-data
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(form_data.username, form_data.password, db)
    access_token = AuthService.create_access_token({"sub": user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


