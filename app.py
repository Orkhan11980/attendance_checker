from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import jwt
from sqlalchemy.exc import SQLAlchemyError
import os

from api.exceptions import (
    database_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    jwt_exception_handler,
    expired_token_exception_handler,
    global_exception_handler
)

from api.controller import (
    auth_controller,
    instructor_controller,
    qr_code_controller
)

app = FastAPI()

# Uncomment exception handlers if needed
# app.add_exception_handler(SQLAlchemyError, database_exception_handler)
# app.add_exception_handler(jwt.DecodeError, jwt_exception_handler)
# app.add_exception_handler(StarletteHTTPException, http_exception_handler)
# app.add_exception_handler(RequestValidationError, validation_exception_handler)
# app.add_exception_handler(jwt.InvalidSignatureError, jwt_exception_handler)
# app.add_exception_handler(jwt.ExpiredSignatureError, expired_token_exception_handler)
# app.add_exception_handler(Exception, global_exception_handler)

API_Route_auth = auth_controller.router
API_Route_instructor = instructor_controller.router
API_Route_qr = qr_code_controller.router

routers = [
    API_Route_auth,
    API_Route_instructor,
    API_Route_qr
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

for route in routers:
    app.include_router(route)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Service is up and running"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # Ensure port matches Dockerfile
