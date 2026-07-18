from app.services.bitbucket_webhook_service import (
    BitbucketWebhookService
)


def main():
    webhook_service = (
        BitbucketWebhookService()
    )

    pull_request_payload = {
        "pullrequest": {
            "id": 1,
            "title": "Add user creation",
            "state": "OPEN",
            "source": {
                "branch": {
                    "name": (
                        "feature/"
                        "add-user-creation"
                    )
                }
            },
            "destination": {
                "branch": {
                    "name": "main"
                }
            }
        },
        "repository": {
            "full_name": (
                "cristian-tfm/"
                "tfm-sample-project"
            )
        }
    }

    result = webhook_service.parse_event(
        event_key="pullrequest:created",
        payload=pull_request_payload
    )

    print(
        "Bitbucket webhook parsing successful"
    )

    print(
        f"Status: {result['status']}"
    )

    print(
        f"Event: {result['event_key']}"
    )

    print(
        "Should review: "
        f"{result['should_review']}"
    )

    print(
        "Pull Request ID: "
        f"{result['pull_request_id']}"
    )

    print(
        f"Title: {result['title']}"
    )

    print(
        f"Repository: {result['repository']}"
    )

    print(
        "Source branch: "
        f"{result['source_branch']}"
    )

    print(
        "Destination branch: "
        f"{result['destination_branch']}"
    )

    ignored_result = (
        webhook_service.parse_event(
            event_key="repo:push",
            payload={
                "repository": {
                    "full_name": (
                        "cristian-tfm/"
                        "tfm-sample-project"
                    )
                }
            }
        )
    )

    print()
    print("Unsupported event test")
    print(
        f"Status: "
        f"{ignored_result['status']}"
    )

    print(
        "Should review: "
        f"{ignored_result['should_review']}"
    )

    print(
        f"Reason: "
        f"{ignored_result['reason']}"
    )


if __name__ == "__main__":
    main()