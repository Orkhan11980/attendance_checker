from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from services.qr_code_service import QRService
from api.schema.qr_schema import QRSessionCreateSchema, QRScanSchema, QRSessionResponseSchema, QRScanResponseSchema, StudentResponseSchema
from config.database import get_db
from config.auth import get_current_instructor, get_current_student

router = APIRouter(prefix="/qr", tags=["QR Code Attendance"])

@router.post("/generate") # response_model=QRSessionResponseSchema
def generate_qr_session(
    data: QRSessionCreateSchema,
    current_instructor=Depends(get_current_instructor),
    db: Session = Depends(get_db)
):
    """Instructor generates a QR session for attendance."""
    qr_session = QRService.generate_qr_session(data, current_instructor.id, db)
    return qr_session

@router.post("/scan", response_model=QRScanResponseSchema)
def scan_qr_code(
    data: QRScanSchema,
    current_student=Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Student scans a QR code for attendance verification."""
    result = QRService.scan_qr(current_student.id, data, db)
    return result


@router.get("/attendance/{qr_session_id}", response_model=List[StudentResponseSchema])
def get_scanned_students(
    qr_session_id: int,
    db: Session = Depends(get_db),
    current_instructor=Depends(get_current_instructor),
    ):
    return QRService.get_scanned_students(qr_session_id, db)