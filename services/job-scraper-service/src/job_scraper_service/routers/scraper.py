from fastapi import APIRouter

from src.job_scraper_service.services.parser_dou import get_dou_vacancies
from src.job_scraper_service.services.parser_work_ua import parse_workua
from src.job_scraper_service.schemas.scraper import ScraperRequest, ScraperResponse

router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/jobs", response_model=ScraperResponse)
async def scrape_jobs(request: ScraperRequest) -> ScraperResponse:
    dou_jobs = get_dou_vacancies(request.query, 5, 0.1, 700)
    work_ua_jobs = parse_workua(request.query, request.pages, 700)
    return ScraperResponse(jobs=dou_jobs + work_ua_jobs[:2])