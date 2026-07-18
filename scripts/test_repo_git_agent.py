from app.agents.bitbucket_agent import BitbucketAgent
from app.agents.repo_git_agent import RepoGitAgent


def main():
    bitbucket_agent = BitbucketAgent()
    repo_git_agent = RepoGitAgent()

    pull_request_context = bitbucket_agent.execute(1)

    result = repo_git_agent.execute(
        pull_request_context
    )

    print("RepoGitAgent execution successful")
    print(f"Agent: {result['agent']}")
    print(
        f"Files analyzed: "
        f"{result['files_analyzed']}"
    )
    print(f"Summary: {result['summary']}")
    print("Findings:")

    for finding in result["findings"]:
        print(
            f"- [{finding['severity']}] "
            f"{finding['file']}:"
            f"{finding['line']} - "
            f"{finding['problem']}"
        )


if __name__ == "__main__":
    main()