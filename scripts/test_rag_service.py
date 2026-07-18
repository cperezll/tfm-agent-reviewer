from app.services.rag_service import RAGService


def main():
    rag_service = RAGService()

    query = (
        "The Pull Request creates a user "
        "and returns the password in plain text"
    )

    results = rag_service.retrieve(
        query=query,
        top_k=3
    )

    print("RAGService execution successful")
    print(
        "Knowledge documents: "
        f"{rag_service.list_documents()}"
    )
    print(f"Query: {query}")
    print("Retrieved context:")

    if not results:
        print("- No relevant context found")
        return

    for result in results:
        print()
        print(
            f'Source: {result["source"]}'
        )
        print(
            f'Chunk: {result["chunk_id"]}'
        )
        print(
            f'Score: {result["score"]}'
        )
        print(
            f'Content: {result["content"]}'
        )


if __name__ == "__main__":
    main()