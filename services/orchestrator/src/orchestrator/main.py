import httpx
from fastapi import FastAPI
from src.orchestrator.schemas import GetJobsRequest, GetJobsResponse

app = FastAPI()


@app.post("/get-jobs", response_model=GetJobsResponse)
async def root(request: GetJobsRequest):
    async with httpx.AsyncClient(timeout=None) as client:
        query_response = await client.post("http://127.0.0.1:8001/queries/generate", json={"resume": request.resume})
        query = query_response.json()["query"]

        jobs_response = await client.post("http://127.0.0.1:8002/scraper/jobs", json={"query": query, "pages": 1})
        similarity_response = await client.post("http://127.0.0.1:8001/jobs/analyze", json={
            "role": "user",
            "vacancy": str(jobs_response.json()),
            "resume": request.resume
        })

        return similarity_response.json()
