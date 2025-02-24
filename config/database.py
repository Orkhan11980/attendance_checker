from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
from api.model.base_model import Base
from api.model.attendance_model import AttendanceRecord, Student, User, Instructor, QRSession, Course, instructor_course
from tenacity import retry, wait_fixed, stop_after_attempt
from urllib.parse import quote

# Load environment variables from .env file
load_dotenv()

# Safely retrieve and validate environment variables
def get_env_var(name: str, default: str = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Environment variable {name} is not set or is None")
    return str(value)  # Ensure the value is a string

try:
    USER = get_env_var("MYSQL_USER")
    PASSWORD = quote(get_env_var("MYSQL_PASSWORD"))  # Quote the password for URL safety
    HOST = get_env_var("MYSQL_HOST")
    PORT = get_env_var("MYSQL_PORT", "3306")  # Default to 3306 if not set
    DATABASE_NAME = get_env_var("MYSQL_DATABASE")
except ValueError as e:
    print(f"Error loading environment variables: {e}")
    raise

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