import logging
from collections.abc import Callable

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    Header,
    HTTPException
)

from app.orchestrator.agent_orchestrator import (
    AgentOrchestrator
)
from app.services.bitbucket_webhook_service import (
    BitbucketWebhookService
)


router = APIRouter(
    tags=["Bitbucket Webhook"]
)

webhook_service = BitbucketWebhookService()

logger = logging.getLogger(__name__)


def get_orchestrator_factory(
) -> Callable[[], AgentOrchestrator]:

    return AgentOrchestrator


def process_pull_request_review(
    orchestrator_factory: Callable[
        [],
        AgentOrchestrator
    ],
    pull_request_id: int
) -> None:

    try:
        orchestrator = orchestrator_factory()

        result = orchestrator.review_pull_request(
            pull_request_id
        )

        logger.info(
            "Automatic review completed. "
            "Pull Request ID: %s. "
            "Status: %s. "
            "Selected agents: %s",
            pull_request_id,
            result.get("review_status"),
            result.get("selected_agents")
        )

    except Exception:
        logger.exception(
            "Automatic review failed for "
            "Pull Request ID: %s",
            pull_request_id
        )


@router.post("/webhook/bitbucket")
def receive_bitbucket_webhook(
    background_tasks: BackgroundTasks,
    payload: dict = Body(...),
    x_event_key: str | None = Header(
        default=None,
        alias="X-Event-Key"
    ),
    orchestrator_factory: Callable[
        [],
        AgentOrchestrator
    ] = Depends(
        get_orchestrator_factory
    )
) -> dict:

    try:
        event_result = webhook_service.parse_event(
            event_key=x_event_key,
            payload=payload
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

    if not event_result["should_review"]:
        return event_result

    pull_request_id = event_result[
        "pull_request_id"
    ]

    background_tasks.add_task(
        process_pull_request_review,
        orchestrator_factory,
        pull_request_id
    )

    return {
        "status": "review_scheduled",
        "event_key": event_result[
            "event_key"
        ],
        "pull_request_id": pull_request_id,
        "repository": event_result[
            "repository"
        ],
        "source_branch": event_result[
            "source_branch"
        ],
        "destination_branch": event_result[
            "destination_branch"
        ],
        "message": (
            "The Pull Request review was "
            "scheduled successfully"
        )
    }