import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.responses import Response

from .api.router import api_router
from .core.config import settings
from .db.base import Base
from .db.session import engine
from sqlalchemy import inspect
from .models import admin_user, collection, product  # noqa: F401


logger = logging.getLogger(__name__)
app = FastAPI(title="Chiniot Furniture Point API", version="1.0.0")


def _configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not root_logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
        return

    for handler in root_logger.handlers:
        handler.setLevel(logging.INFO)


_configure_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    start_time = time.perf_counter()
    logger.info("request_start method=%s path=%s query=%s", request.method, request.url.path, request.url.query)

    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed method=%s path=%s", request.method, request.url.path)
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "request_end method=%s path=%s status=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(
        "validation_error method=%s path=%s errors=%s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error method=%s path=%s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
def on_startup() -> None:
    try:
        logger.info("startup_begin")
        # Try connecting to the DB and inspect tables
        with engine.connect() as conn:
            inspector = inspect(conn)
            tables = inspector.get_table_names()

        if tables:
            logger.info("startup_db_connected tables=%s", tables)
        else:
            # No tables found, create from metadata
            Base.metadata.create_all(bind=engine)
            with engine.connect() as conn:
                inspector = inspect(conn)
                created = inspector.get_table_names()
            logger.info("startup_db_created tables=%s", created)
    except Exception as exc:
        logger.exception("startup_failed error=%s", exc)
        raise


app.include_router(api_router, prefix="/api")