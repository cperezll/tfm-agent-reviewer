import sys

from requests.exceptions import RequestException

from app.services.bitbucket_service import BitbucketService


def main():
    try:
        bitbucket_service = BitbucketService()

        pull_request_id = 1

        pull_request = bitbucket_service.get_pull_request(
            pull_request_id
        )

        pull_request_diff = bitbucket_service.get_pull_request_diff(
            pull_request_id
        )

        print("Connection successful")
        print(f"Pull Request ID: {pull_request['id']}")
        print(f"Title: {pull_request['title']}")
        print(f"State: {pull_request['state']}")
        print(
            "Source branch: "
            f"{pull_request['source']['branch']['name']}"
        )
        print(
            "Destination branch: "
            f"{pull_request['destination']['branch']['name']}"
        )
        print(f"Diff length: {len(pull_request_diff)} characters")

    except ValueError as error:
        print(f"Configuration error: {error}")
        sys.exit(1)

    except RequestException as error:
        print(f"Bitbucket connection error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()