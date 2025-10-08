from fastapi import APIRouter

from src.llm_service.core.logger import logger
from src.llm_service.services.pipeline import pipeline
from src.llm_service.utils.prompts import load_prompt
from src.llm_service.schemas.queries import VacancyRequest, QueryGeneratorResponse

router = APIRouter(prefix="/queries", tags=["Query Generator"])


@router.post("/generate", response_model=QueryGeneratorResponse)
async def generate_query(vacancy: VacancyRequest) -> QueryGeneratorResponse:
    system_prompt = await load_prompt("query_prompt.txt")

    generate = pipeline.generate(vacancy.resume, system_prompt)

    return QueryGeneratorResponse(query=generate)
