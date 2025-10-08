from fastapi import APIRouter, HTTPException

from src.llm_service.core.logger import logger
from src.llm_service.services.pipeline import pipeline
from src.llm_service.utils.prompts import load_prompt
from src.llm_service.utils.json_utils import safe_json_parse
from src.llm_service.schemas.jobs import JobsRequest, JobsResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/analyze", response_model=JobsResponse)
async def compare_skills(request: JobsRequest) -> JobsResponse:
    retries = 5

    system_prompt = await load_prompt("analyze_jobs.txt")

    prompt = f"Resume: {request.resume}\n\nVacancy: {request.vacancy}"

    for i in range(retries):
        generate = pipeline.generate(prompt, system_prompt)
        print(generate)
        try:
            validate_json = safe_json_parse(generate)
            return JobsResponse(**validate_json)
        except ValueError:
            logger.error(f"Failed to parse JSON response", exc_info=True)
            logger.info(f"Retrying... {i}/{retries}")
            continue
        except Exception as e:
            logger.error(f"Failed to generate response: ", exc_info=True)
            continue

    raise HTTPException(status_code=422, detail="Failed to generate response")


@router.post("/match")
async def match():
    pass
