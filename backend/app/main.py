from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.access import PUBLIC_PATHS, resolve_owner, set_owner
from app.api.library_routes import router as library_router
from app.api.media import router as media_router
from app.api.projects import router as projects_router
from app.api.studio import router as studio_router
from app.api.workflow import router as workflow_router
from app.core.config import get_settings
from app.core.database import get_engine, session_scope


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_engine()
    from app.services.jobs import recover_jobs

    recover_jobs()
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
    app.include_router(studio_router, prefix="/api")
    app.include_router(library_router, prefix="/api")
    app.include_router(media_router, prefix="/api")

    @app.middleware("http")
    async def attach_owner(request: Request, call_next):
        if request.method == "OPTIONS" or not request.url.path.startswith("/api") or request.url.path in PUBLIC_PATHS:
            set_owner("local")
            return await call_next(request)
        try:
            with session_scope() as session:
                owner = resolve_owner(request, session)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        set_owner(owner)
        return await call_next(request)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request, exc: RequestValidationError) -> JSONResponse:
        message = "Check the form and try again."
        errors = exc.errors()
        if errors:
            message = str(errors[0].get("msg", message)).removeprefix("Value error, ")
        return JSONResponse(status_code=422, content={"detail": message})

    return app


app = create_app()
