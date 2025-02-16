from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
# import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError
import jwt

# logger = logging.getLogger(__name__)

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Database integrity error",
                "status_code": status.HTTP_409_CONFLICT
            }
        )
    elif isinstance(exc, OperationalError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "detail": "Database connection error",
                "status_code": status.HTTP_503_SERVICE_UNAVAILABLE
            }
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # logger.error(f"HTTP Exception: {exc.detail}", exc_info=True)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # logger.error(f"Validation Error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )
async def jwt_exception_handler(request: Request, exc: Exception):
    # logger.error(f"JWT Error: {str(exc)}", exc_info=True)

    if isinstance(exc, jwt.InvalidSignatureError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Invalid token signature",
                "status_code": status.HTTP_401_UNAUTHORIZED
            }
        )
    elif isinstance(exc, jwt.DecodeError):  
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": "Invalid token format",
                "status_code": status.HTTP_401_UNAUTHORIZED
            }
        )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Invalid token format or signature",
            "status_code": status.HTTP_401_UNAUTHORIZED
        }
    )

async def expired_token_exception_handler(request: Request, exc: ExpiredSignatureError):
    # logger.error("Token Expired Error", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": "Token has expired",
            "status_code": status.HTTP_401_UNAUTHORIZED
        }
    )

async def global_exception_handler(request: Request, exc: Exception):

    # logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )