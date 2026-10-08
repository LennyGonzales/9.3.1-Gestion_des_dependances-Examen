from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.wakeup import router as wakeup_router
from app.container import container
from app.domain.exceptions import DomainError, UserNotFoundError


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await container.init_resources()
    yield
    await container.shutdown_resources()


app = FastAPI(title="Réveil musical API", version="0.1.0", lifespan=lifespan)
container.wire(modules=["app.api.routes.wakeup"])
app.include_router(wakeup_router)


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(
    _request: Request, exc: UserNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "userId": exc.user_id},
    )


@app.exception_handler(DomainError)
async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
