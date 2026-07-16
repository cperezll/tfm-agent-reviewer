import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

email = os.getenv("BITBUCKET_EMAIL")
api_token = os.getenv("BITBUCKET_API_TOKEN")
workspace = os.getenv("BITBUCKET_WORKSPACE")
repository = os.getenv("BITBUCKET_REPOSITORY")
pull_request_id = os.getenv("BITBUCKET_PULL_REQUEST_ID")

required_variables = {
    "BITBUCKET_EMAIL": email,
    "BITBUCKET_API_TOKEN": api_token,
    "BITBUCKET_WORKSPACE": workspace,
    "BITBUCKET_REPOSITORY": repository,
    "BITBUCKET_PULL_REQUEST_ID": pull_request_id,
}

missing_variables = [
    name for name, value in required_variables.items() if not value
]

if missing_variables:
    print("Missing environment variables:")
    for variable in missing_variables:
        print(f"- {variable}")
    sys.exit(1)

url = (
    f"https://api.bitbucket.org/2.0/repositories/"
    f"{workspace}/{repository}/pullrequests/{pull_request_id}"
)

try:
    response = requests.get(
        url,
        auth=(email, api_token),
        timeout=30,
    )

    response.raise_for_status()
    pull_request = response.json()

    print("Connection successful")
    print(f"Pull Request ID: {pull_request['id']}")
    print(f"Title: {pull_request['title']}")
    print(f"State: {pull_request['state']}")
    print(f"Source branch: {pull_request['source']['branch']['name']}")
    print(
        "Destination branch: "
        f"{pull_request['destination']['branch']['name']}"
    )

except requests.exceptions.HTTPError:
    print(f"Bitbucket returned HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

except requests.exceptions.RequestException as error:
    print(f"Connection error: {error}")
    sys.exit(1)