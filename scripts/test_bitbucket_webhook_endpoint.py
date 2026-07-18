from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.webhook_routes import (
    get_orchestrator_factory,
    router
)


class FakeAgentOrchestrator:

    def __init__(self):
        self.received_pull_requests = []

    def review_pull_request(
        self,
        pull_request_id: int
    ) -> dict:

        self.received_pull_requests.append(
            pull_request_id
        )

        return {
            "review_status": "review_published",
            "selected_agents": [
                "BitbucketAgent",
                "RepoGitAgent",
                "RAGAgent"
            ]
        }


app = FastAPI()
app.include_router(router)

fake_orchestrator = FakeAgentOrchestrator()


def create_fake_orchestrator(
) -> FakeAgentOrchestrator:

    return fake_orchestrator


app.dependency_overrides[
    get_orchestrator_factory
] = lambda: create_fake_orchestrator

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
        "Accepted webhook orchestration test"
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
        "Pull Request ID: "
        f'{accepted_result["pull_request_id"]}'
    )

    print(
        "Fake orchestrator calls: "
        f"{fake_orchestrator.received_pull_requests}"
    )

    assert (
        accepted_response.status_code == 200
    )

    assert (
        accepted_result["status"]
        == "review_scheduled"
    )

    assert (
        fake_orchestrator
        .received_pull_requests
        == [1]
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

    ignored_result = (
        ignored_response.json()
    )

    print()
    print("Ignored webhook event test")

    print(
        "HTTP status: "
        f"{ignored_response.status_code}"
    )

    print(
        "Webhook status: "
        f'{ignored_result["status"]}'
    )

    print(
        "Fake orchestrator calls: "
        f"{fake_orchestrator.received_pull_requests}"
    )

    assert (
        ignored_response.status_code == 200
    )

    assert (
        ignored_result["status"]
        == "ignored"
    )

    assert (
        fake_orchestrator
        .received_pull_requests
        == [1]
    )

    invalid_response = client.post(
        "/webhook/bitbucket",
        json=payload
    )

    invalid_result = (
        invalid_response.json()
    )

    print()
    print("Invalid webhook event test")

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
        "Webhook and orchestrator "
        "connection test successful"
    )


if __name__ == "__main__":
    main()