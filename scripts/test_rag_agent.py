from app.agents.bitbucket_agent import BitbucketAgent
from app.agents.rag_agent import RAGAgent


def main():
    bitbucket_agent = BitbucketAgent()
    rag_agent = RAGAgent()

    pull_request_context = (
        bitbucket_agent.execute(1)
    )

    result = rag_agent.execute(
        pull_request_context
    )

    print("RAGAgent execution successful")
    print(f"Agent: {result['agent']}")
    print(
        f"Context found: "
        f"{result['context_found']}"
    )
    print(
        f"Documents used: "
        f"{result['documents_used']}"
    )

    print("\nRetrieved context:")

    for context in result[
        "retrieved_context"
    ]:
        print(
            f"- {context['source']} "
            f"(chunk {context['chunk_id']}, "
            f"score {context['score']})"
        )

        print(
            f"  {context['content']}"
        )

    print("\nRAGAgent analysis:")
    print(result["analysis"])


if __name__ == "__main__":
    main()