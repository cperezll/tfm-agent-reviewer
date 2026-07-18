class BitbucketWebhookService:

    REVIEW_EVENTS = (
        "pullrequest:created",
        "pullrequest:updated"
    )

    def parse_event(
        self,
        event_key: str,
        payload: dict
    ) -> dict:

        if not event_key:
            raise ValueError(
                "Bitbucket event key is required"
            )

        if not isinstance(payload, dict):
            raise ValueError(
                "Bitbucket webhook payload "
                "must be a dictionary"
            )

        if event_key not in self.REVIEW_EVENTS:
            return {
                "status": "ignored",
                "event_key": event_key,
                "should_review": False,
                "reason": (
                    "The event does not require "
                    "a Pull Request review"
                )
            }

        pull_request = payload.get(
            "pullrequest"
        )

        if not isinstance(
            pull_request,
            dict
        ):
            raise ValueError(
                "Pull Request information "
                "is missing from the webhook"
            )

        pull_request_id = pull_request.get(
            "id"
        )

        if not isinstance(
            pull_request_id,
            int
        ):
            raise ValueError(
                "Pull Request ID is missing "
                "or invalid"
            )

        repository = payload.get(
            "repository",
            {}
        )

        source = pull_request.get(
            "source",
            {}
        )

        destination = pull_request.get(
            "destination",
            {}
        )

        source_branch = (
            source
            .get("branch", {})
            .get("name")
        )

        destination_branch = (
            destination
            .get("branch", {})
            .get("name")
        )

        return {
            "status": "accepted",
            "event_key": event_key,
            "should_review": True,
            "pull_request_id": pull_request_id,
            "title": pull_request.get(
                "title",
                ""
            ),
            "state": pull_request.get(
                "state",
                ""
            ),
            "repository": repository.get(
                "full_name",
                ""
            ),
            "source_branch": source_branch,
            "destination_branch": (
                destination_branch
            )
        }