from pydantic import BaseModel


class GetJobsRequest(BaseModel):
    resume: str


class Job(BaseModel):
    title: str
    matching_skills: list[str | None]
    vacancy_link: str


class GetJobsResponse(BaseModel):
    summary: str
    results: list[Job]
