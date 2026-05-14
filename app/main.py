from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .api.router import api_router
from .db.base import Base
from .db.session import engine
from sqlalchemy import inspect
from .models import admin_user, collection, product  # noqa: F401


logger = logging.getLogger(__name__)
app = FastAPI(title="Chiniot Furniture Point API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    try:
        # Try connecting to the DB and inspect tables
        with engine.connect() as conn:
            inspector = inspect(conn)
            tables = inspector.get_table_names()

        if tables:
            logger.info(f"Database connected. Tables present: {tables}")
        else:
            # No tables found, create from metadata
            Base.metadata.create_all(bind=engine)
            with engine.connect() as conn:
                inspector = inspect(conn)
                created = inspector.get_table_names()
            logger.info(f"No tables found. Created tables: {created}")
    except Exception as exc:
        logger.exception("Database connection or migration failed: %s", exc)
        raise


app.include_router(api_router, prefix="/api")