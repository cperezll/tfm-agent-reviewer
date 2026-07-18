from app.orchestrator.agent_orchestrator import AgentOrchestrator

def main():
    orchestrator = AgentOrchestrator()

    result = orchestrator.review_pull_request(1)

    print("AgentOrchestrator execution successful")
    print(f"Orchestrator: {result['orchestrator']}")
    print(f"Pull Request ID: {result['pull_request_id']}")
    print(f"Selected agents: {result['selected_agents']}")
    print(f"Review status: {result['review_status']}")

    bitbucket_context = result["context"]["bitbucket"]

    print(f"Title: {bitbucket_context['title']}")
    print(f"State: {bitbucket_context['state']}")
    print(
        f"Diff length: "
        f"{len(bitbucket_context['diff'])} characters"
    )

if __name__ == "__main__":
    main()