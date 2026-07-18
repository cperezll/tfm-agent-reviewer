from app.agents.bitbucket_agent import BitbucketAgent
from app.services.diff_service import DiffService


def main():
    bitbucket_agent = BitbucketAgent()
    diff_service = DiffService()

    context = bitbucket_agent.execute(1)

    added_lines = diff_service.extract_added_lines(
        context["diff"]
    )

    print("Added lines found")
    print("-----------------")

    for added_line in added_lines:
        print(
            f'{added_line["file"]}:'
            f'{added_line["line"]} -> '
            f'{added_line["code"]}'
        )


if __name__ == "__main__":
    main()