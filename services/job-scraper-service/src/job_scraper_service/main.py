from fastapi import FastAPI
from src.job_scraper_service.routers.scraper import router as scraper_router


def get_application():
    app = FastAPI()

    app.include_router(scraper_router)

    return app


app = get_application()
