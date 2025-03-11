
# auth_service.py
from datetime import datetime, timedelta
from passlib.context import CryptContext
from config.database import get_db
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from fastapi import HTTPException, status
from jose import jwt
from api.model.attendance_model import User
from api.schema.registration_schema import LoginSchema

load_dotenv()

# Get values from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default to HS256 if not found
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def authenticate_user(email: str, password: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user or not AuthService.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # @staticmethod
    # def login_user(data: LoginSchema, db: Session):
    #     user = AuthService.authenticate_user(data, db)
    #     access_token = AuthService.create_access_token({"sub": user.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    #     return {"access_token": access_token, "token_type": "bearer"}
