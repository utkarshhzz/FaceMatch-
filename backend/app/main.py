"""
FastAPI application factory.

Wires together:
  - logging
  - the API router (/api/v1)
  - CORS (so the React frontend on :5173 can call us on :8000)
  - startup: create DB tables + seed the root admin
  - global exception handlers
"""
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import app_logger, setup_logging


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ---------- CORS ----------
    # Tells the browser: "responses from this API may be read by these origins."
    # Without this, the React app on :5173 gets a CORS error calling :8000.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,  # e.g. ["http://localhost:5173"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------- Startup: create tables + seed admin ----------
    @app.on_event("startup")
    async def on_startup() -> None:
        app_logger.info("Starting service: {}", settings.APP_NAME)
        try:
            # Import inside to keep module import cheap and isolate failures.
            from app.db.init_db import init_db
            await init_db()
        except Exception as e:  # noqa: BLE001
            # DB may not be up yet (e.g. during a quick dev restart). We log
            # loudly but do NOT crash the app — endpoints will return 500 on
            # first DB use, which is clearer than a silent boot failure.
            app_logger.error("DB init failed (tables/admin may be missing): {}", e)

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        app_logger.info("Shutting down service {}", settings.APP_NAME)

    # ---------- Request logging middleware ----------
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        request_id = str(uuid4())
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_time = (time.perf_counter() - start) * 1000
            app_logger.exception(
                "Request {} {} failed after {:.2f}ms",
                request.method, request.url, elapsed_time,
            )
            raise
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-request-id"] = request_id
        app_logger.info(
            "request_id={} method={} path={} status={} latency_ms={:.2f}",
            request_id, request.method, request.url.path,
            response.status_code, elapsed_ms,
        )
        return response

    # ---------- Exception handlers ----------
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError,
    ) -> JSONResponse:
        app_logger.warning(
            "Validation error on {} {}: {}",
            request.method, request.url.path, exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation failed", "errors": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        app_logger.warning(
            "HTTP error on {} {}: {} detail-{}",
            request.method, request.url.path, exc.status_code, exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        app_logger.exception("Unhandled error on {} {}", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # ---------- Routes ----------
    app.include_router(api_router, prefix=settings.APP_V1_PREFIX)
    return app


app = create_app()
