import os
import requests
from dotenv import load_dotenv

load_dotenv()

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
                f"Missing Bitbucket environment variables: {missing_text}"
            )

    def get_pull_request(self, pull_request_id):
        url = f"{self.base_url}/pullrequests/{pull_request_id}"

        response = requests.get(
            url,
            auth=(self.email, self.api_token),
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_pull_request_diff(self, pull_request_id):
        url = f"{self.base_url}/pullrequests/{pull_request_id}/diff"

        response = requests.get(
            url,
            auth=(self.email, self.api_token),
            timeout=30,
        )

        response.raise_for_status()

        return response.text