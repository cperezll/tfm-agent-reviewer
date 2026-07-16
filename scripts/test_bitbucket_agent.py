from app.agents.bitbucket_agent import BitbucketAgent

def main():
    agent = BitbucketAgent()

    result = agent.execute(1)

    print("BitbucketAgent execution successful")
    print(f"Agent: {result['agent']}")
    print(f"Pull Request ID: {result['pull_request_id']}")
    print(f"Title: {result['title']}")
    print(f"Author: {result['author']}")
    print(f"Source branch: {result['source_branch']}")
    print(f"Destination branch: {result['destination_branch']}")
    print(f"Diff length: {len(result['diff'])} characters")


if __name__ == "__main__":
    main()