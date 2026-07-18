import os

import requests
from dotenv import load_dotenv


load_dotenv(override=True)


class BitbucketService:

    def __init__(self):
        self.email = os.getenv("BITBUCKET_EMAIL")
        self.api_token = os.getenv("BITBUCKET_API_TOKEN")
        self.workspace = os.getenv("BITBUCKET_WORKSPACE")
        self.repository = os.getenv("BITBUCKET_REPOSITORY")

        self._validate_configuration()

        self.base_url = (
            "https://api.bitbucket.org/2.0/repositories/"
            f"{self.workspace}/{self.repository}"
        )

    def _validate_configuration(self):
        required_variables = {
            "BITBUCKET_EMAIL": self.email,
            "BITBUCKET_API_TOKEN": self.api_token,
            "BITBUCKET_WORKSPACE": self.workspace,
            "BITBUCKET_REPOSITORY": self.repository,
        }

        missing_variables = []

        for variable_name, variable_value in required_variables.items():
            if not variable_value:
                missing_variables.append(variable_name)

        if missing_variables:
            missing_text = ", ".join(missing_variables)

            raise ValueError(
                "Missing Bitbucket environment variables: "
                f"{missing_text}"
            )

    def _get_paginated_values(
        self,
        url: str
    ) -> list[dict]:

        values = []
        next_url = url

        while next_url:
            response = requests.get(
                next_url,
                auth=(self.email, self.api_token),
                timeout=30
            )

            response.raise_for_status()

            response_data = response.json()

            values.extend(
                response_data.get("values", [])
            )

            next_url = response_data.get("next")

        return values

    def get_pull_request(
        self,
        pull_request_id: int
    ) -> dict:

        url = (
            f"{self.base_url}/pullrequests/"
            f"{pull_request_id}"
        )

        response = requests.get(
            url,
            auth=(self.email, self.api_token),
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def get_pull_request_diff(
        self,
        pull_request_id: int
    ) -> str:

        url = (
            f"{self.base_url}/pullrequests/"
            f"{pull_request_id}/diff"
        )

        response = requests.get(
            url,
            auth=(self.email, self.api_token),
            timeout=30
        )

        response.raise_for_status()

        return response.text

    def get_pull_request_comments(
        self,
        pull_request_id: int
    ) -> list[dict]:

        url = (
            f"{self.base_url}/pullrequests/"
            f"{pull_request_id}/comments"
            "?pagelen=100"
        )

        return self._get_paginated_values(url)

    def get_pull_request_tasks(
        self,
        pull_request_id: int
    ) -> list[dict]:

        url = (
            f"{self.base_url}/pullrequests/"
            f"{pull_request_id}/tasks"
            "?pagelen=100"
        )

        return self._get_paginated_values(url)

    def post_pull_request_comment(
        self,
        pull_request_id: int,
        comment: str
    ) -> dict:

        url = (
            f"{self.base_url}/pullrequests/"
            f"{pull_request_id}/comments"
        )

        payload = {
            "content": {
                "raw": comment
            }
        }

        response = requests.post(
            url,
            auth=(self.email, self.api_token),
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def post_pull_request_inline_comment(
        self,
        pull_request_id: int,
        file_path: str,
        line_number: int,
        comment: str
    ) -> dict:

        url = (
            f"{self.base_url}/pullrequests/"
            f"{pull_request_id}/comments"
        )

        payload = {
            "content": {
                "raw": comment
            },
            "inline": {
                "path": file_path,
                "to": line_number
            }
        }

        response = requests.post(
            url,
            auth=(self.email, self.api_token),
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def create_pull_request_task(
        self,
        pull_request_id: int,
        comment_id: int,
        task_content: str
    ) -> dict:

        url = (
            f"{self.base_url}/pullrequests/"
            f"{pull_request_id}/tasks"
        )

        payload = {
            "content": {
                "raw": task_content
            },
            "comment": {
                "id": comment_id
            }
        }

        response = requests.post(
            url,
            auth=(self.email, self.api_token),
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        return response.json()