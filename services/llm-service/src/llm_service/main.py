from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.llm_service.services.pipeline import LLMPipeline
from src.llm_service.core.logger import logger
from src.llm_service.core.config import config
from src.llm_service.routers.jobs import router as compare_router
from src.llm_service.routers.queries import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    pipeline = LLMPipeline(config.llm_config)
    pipeline.load_model()

    logger.info("[LLMPipeline] started")
    yield

    logger.info("Application stopped")


def get_application():
    app = FastAPI(lifespan=lifespan, **config.app_config.model_dump())

    app.include_router(compare_router)
    app.include_router(query_router)

    return app


app = get_application()
