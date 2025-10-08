from pydantic import BaseModel


class ScraperRequest(BaseModel):
    query: str
    pages: int

class Job(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    description: str
    link: str

class ScraperResponse(BaseModel):
    jobs: list[Job]