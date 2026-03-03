from fastapi import FastAPI

from app.api.exception_handlers import domain_exception_handler
from app.api.routers.accounts import router as account_router
from app.api.routers.transactions import router as transaction_router
from app.domain.exceptions import DomainException

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.add_exception_handler(
    DomainException,
    domain_exception_handler,
)


app.include_router(account_router)
app.include_router(transaction_router)