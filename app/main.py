from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from requests.exceptions import RequestException

from app.api.webhook_routes import (
    router as webhook_router
)
from app.orchestrator.agent_orchestrator import (
    AgentOrchestrator
)


app = FastAPI(
    title="TFM Agent Reviewer",
    description=(
        "Agent-based Pull Request "
        "review prototype"
    ),
    version="0.1.0"
)

app.include_router(
    webhook_router
)


class PullRequestReviewRequest(BaseModel):
    pull_request_id: int


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": (
            "TFM Agent Reviewer is running"
        )
    }


@app.post("/review/pr")
def review_pull_request(
    request: PullRequestReviewRequest
):
    try:
        orchestrator = AgentOrchestrator()

        result = (
            orchestrator
            .review_pull_request(
                request.pull_request_id
            )
        )

        return {
            "status": result[
                "review_status"
            ],
            "result": result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        ) from error

    except RequestException as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "Bitbucket connection error: "
                f"{error}"
            )
        ) from error