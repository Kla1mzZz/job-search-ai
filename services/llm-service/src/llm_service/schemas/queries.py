from pydantic import BaseModel


class VacancyRequest(BaseModel):
    resume: str


class QueryGeneratorResponse(BaseModel):
    query: str
