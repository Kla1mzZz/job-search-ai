from pydantic import BaseModel


class JobsRequest(BaseModel):
    role: str
    resume: str
    vacancy: str


class Job(BaseModel):
    title: str
    matching_skills: list[str | None]
    vacancy_link: str


class JobsResponse(BaseModel):
    summary: str
    results: list[Job]
