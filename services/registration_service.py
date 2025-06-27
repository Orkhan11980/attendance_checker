from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.model.attendance_model import User, Student, Instructor, get_baku_time
from api.schema.registration_schema import StudentRegisterSchema, InstructorRegisterSchema
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def register_student(data: StudentRegisterSchema, db: Session):
        try:
            # Check if the user already exists
            existing_user = db.query(User).filter(User.email == data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered.."
                )
            # Check if student_id already exists
            existing_student_id = db.query(Student).filter(Student.student_id == data.student_id).first()
            if existing_student_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student ID already registered"
                )

            # Check if phone_id already exists
            existing_phone_id = db.query(Student).filter(Student.phone_id == data.phone_id).first()
            if existing_phone_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone ID already registered"
                )
            
            # Hash the password
            hashed_password = RegisterService.hash_password(data.password)

            # Create the user (but don't commit yet)
            current_time = get_baku_time()
            user = User(
                email=data.email,
                password=hashed_password,
                first_name=data.first_name,
                last_name=data.last_name,
                role="student",
                created_at=current_time,
                updated_at=current_time
            )
            db.add(user)
            db.flush()  # Assigns an ID to the user without committing

            # Create student record (but don't commit yet)
            student = Student(
                user_id=user.id,
                student_id=data.student_id,
                phone_id=data.phone_id,
                phone_model=data.phone_model,
                registered_at=current_time
            )
            db.add(student)
            db.flush()  # Assigns an ID to the student without committing

            # Commit both changes together
            db.commit()

            # Refresh the objects to get the latest data
            db.refresh(user)
            db.refresh(student)

            return {"success": True, "user_id": user.id, "student_id": student.id}

        except SQLAlchemyError as e:
            # Rollback the transaction in case of any database error
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while registering the student"
            )


    @staticmethod
    def register_instructor(data: InstructorRegisterSchema, db: Session):
        try:
            # Check if the user already exists
            existing_user = db.query(User).filter(User.email == data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            existing_instructor_id = db.query(Instructor).filter(Instructor.instructor_id == data.instructor_id).first()
            if existing_instructor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Instructor ID already registered"
                )

            # Hash the password
            hashed_password = RegisterService.hash_password(data.password)

            # Create the user with explicit time
            current_time = get_baku_time()
            user = User(
                email=data.email,
                password=hashed_password,
                first_name=data.first_name,
                last_name=data.last_name,
                role="instructor",
                created_at=current_time,
                updated_at=current_time
            )
            db.add(user)
            db.flush()  

            instructor = Instructor(
                user_id=user.id,
                instructor_id=data.instructor_id,
                department=data.department
            )
            db.add(instructor)
            db.flush() 

            db.commit()

            db.refresh(user)
            db.refresh(instructor)

            return {"success": True, "user_id": user.id, "instructor_id": instructor.id}

        except SQLAlchemyError as e:
            # Rollback the transaction in case of any database error
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while registering the instructor"
            )
    
        # except Exception as e:
        #     # Rollback the transaction in case of any other error
        #     db.rollback()
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail=str(e)
        #     )