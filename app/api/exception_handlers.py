from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.domain.exceptions import DomainException


async def domain_exception_handler(
    request: Request,
    exc: DomainException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,  # instead of 422 (pydantic default)
        content={
            "detail": exc.errors()
        }
    )