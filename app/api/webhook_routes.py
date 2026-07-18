from fastapi import (
    APIRouter,
    Body,
    Header,
    HTTPException
)

from app.services.bitbucket_webhook_service import (
    BitbucketWebhookService
)


router = APIRouter(
    tags=["Bitbucket Webhook"]
)

webhook_service = BitbucketWebhookService()


@router.post("/webhook/bitbucket")
def receive_bitbucket_webhook(
    payload: dict = Body(...),
    x_event_key: str | None = Header(
        default=None,
        alias="X-Event-Key"
    )
) -> dict:

    try:
        result = webhook_service.parse_event(
            event_key=x_event_key,
            payload=payload
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error