from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.webhook_routes import router


app = FastAPI()
app.include_router(router)

client = TestClient(app)


def build_pull_request_payload() -> dict:

    return {
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


def main():

    payload = build_pull_request_payload()

    accepted_response = client.post(
        "/webhook/bitbucket",
        headers={
            "X-Event-Key": (
                "pullrequest:created"
            )
        },
        json=payload
    )

    accepted_result = (
        accepted_response.json()
    )

    print(
        "Accepted webhook endpoint test"
    )

    print(
        "HTTP status: "
        f"{accepted_response.status_code}"
    )

    print(
        "Webhook status: "
        f'{accepted_result["status"]}'
    )

    print(
        "Should review: "
        f'{accepted_result["should_review"]}'
    )

    print(
        "Pull Request ID: "
        f'{accepted_result["pull_request_id"]}'
    )

    print(
        "Repository: "
        f'{accepted_result["repository"]}'
    )

    assert (
        accepted_response.status_code == 200
    )

    assert (
        accepted_result["status"]
        == "accepted"
    )

    assert (
        accepted_result["should_review"]
        is True
    )

    ignored_response = client.post(
        "/webhook/bitbucket",
        headers={
            "X-Event-Key": "repo:push"
        },
        json={
            "repository": {
                "full_name": (
                    "cristian-tfm/"
                    "tfm-sample-project"
                )
            }
        }
    )

    ignored_result = ignored_response.json()

    print()
    print("Ignored webhook endpoint test")

    print(
        "HTTP status: "
        f"{ignored_response.status_code}"
    )

    print(
        "Webhook status: "
        f'{ignored_result["status"]}'
    )

    print(
        "Should review: "
        f'{ignored_result["should_review"]}'
    )

    assert (
        ignored_response.status_code == 200
    )

    assert (
        ignored_result["status"]
        == "ignored"
    )

    assert (
        ignored_result["should_review"]
        is False
    )

    invalid_response = client.post(
        "/webhook/bitbucket",
        json=payload
    )

    invalid_result = invalid_response.json()

    print()
    print("Invalid webhook endpoint test")

    print(
        "HTTP status: "
        f"{invalid_response.status_code}"
    )

    print(
        "Error: "
        f'{invalid_result["detail"]}'
    )

    assert (
        invalid_response.status_code == 400
    )

    print()
    print(
        "Bitbucket webhook endpoint "
        "test successful"
    )


if __name__ == "__main__":
    main()