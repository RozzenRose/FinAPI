from fastapi import Request
from fastapi.responses import JSONResponse
from app.domain.exceptions import DomainException


async def domain_exception_handler(
    request: Request,
    exc: DomainException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )