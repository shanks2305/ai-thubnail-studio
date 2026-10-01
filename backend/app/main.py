from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.media import router as media_router
from app.api.projects import router as projects_router
from app.api.workflow import router as workflow_router
from app.core.config import get_settings
from app.core.database import get_engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_engine()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="AI Thumbnail Suite", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(projects_router, prefix="/api")
    app.include_router(workflow_router, prefix="/api")
    app.include_router(media_router, prefix="/api")

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request, exc: RequestValidationError) -> JSONResponse:
        message = "Check the form and try again."
        errors = exc.errors()
        if errors:
            message = str(errors[0].get("msg", message)).removeprefix("Value error, ")
        return JSONResponse(status_code=422, content={"detail": message})

    return app


app = create_app()
