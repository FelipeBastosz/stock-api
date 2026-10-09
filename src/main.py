import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from src.core.config import settings
from src.core.handlers import global_exception_handler, register_exception_handlers
from src.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Iniciando {settings.PROJECT_NAME} ({settings.ENV})")
    yield
    logger.info("Encerrando aplicação...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para gerenciamento de estoque, produtos, fornecedores e movimentações.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Sistema", "description": "Status e integridade da API"},
        {"name": "Categorias", "description": "Gerenciamento de categorias"},
        {"name": "Fornecedores", "description": "Gerenciamento de fornecedores"},
        {"name": "Produtos", "description": "Catálogo de produtos e controle de estoque"},
        {"name": "Movimentações", "description": "Histórico e auditoria de movimentações"},
    ],
)

register_exception_handlers(app)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.2f}ms)"
        )
        return response
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.opt(exception=exc).error(
            f"{request.method} {request.url.path} falhou após {duration_ms:.2f}ms: {exc}"
        )
        return await global_exception_handler(request, exc)


@app.get("/health", tags=["Sistema"])
async def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }