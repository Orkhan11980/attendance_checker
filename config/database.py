from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from api.model.base_model import Base
from api.model.attendance_model import AttendanceRecord, Student, User, Instructor, QRSession, Course, instructor_course
from tenacity import retry, wait_fixed, stop_after_attempt
from urllib.parse import quote
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

USER = os.getenv("MYSQL_USER")
PASSWORD = quote(os.getenv("MYSQL_PASSWORD"))
HOST = os.getenv("MYSQL_HOST")
PORT = os.getenv("MYSQL_PORT")
DATABASE_NAME = os.getenv("MYSQL_DATABASE")

@retry(wait=wait_fixed(2), stop=stop_after_attempt(30))
def connect_to_database():
    try:
        DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        # Test the connection using text()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
        raise

engine = connect_to_database()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@retry(wait=wait_fixed(2), stop=stop_after_attempt(10))
def initialize_database():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

# Initialize the database tables
initialize_database()