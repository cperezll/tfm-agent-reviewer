from app.services.bitbucket_service import BitbucketService

class BitbucketAgent:

    def __init__(self):
        self.bitbucket_service = BitbucketService()

    def execute(self, pull_request_id: int) -> dict:
        pull_request = self.bitbucket_service.get_pull_request(
            pull_request_id
        )

        pull_request_diff = (
            self.bitbucket_service.get_pull_request_diff(
                pull_request_id
            )
        )

        return {
            "agent": "BitbucketAgent",
            "pull_request_id": pull_request["id"],
            "title": pull_request["title"],
            "description": pull_request.get("description", ""),
            "author": pull_request["author"]["display_name"],
            "state": pull_request["state"],
            "source_branch": (
                pull_request["source"]["branch"]["name"]
            ),
            "destination_branch": (
                pull_request["destination"]["branch"]["name"]
            ),
            "diff": pull_request_diff,
        }