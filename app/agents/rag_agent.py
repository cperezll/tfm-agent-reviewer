import json

from app.services.llm_service import LLMService
from app.services.rag_service import RAGService


class RAGAgent:

    def __init__(self):
        self.rag_service = RAGService()
        self.llm_service = LLMService()

    def execute(
        self,
        pull_request_context: dict
    ) -> dict:

        title = pull_request_context.get(
            "title",
            ""
        )

        description = pull_request_context.get(
            "description",
            ""
        )

        diff = pull_request_context.get(
            "diff",
            ""
        )

        if not diff:
            raise ValueError(
                "Pull Request diff is required"
            )

        query = self._build_query(
            title=title,
            description=description,
            diff=diff
        )

        retrieved_context = (
            self.rag_service.retrieve(
                query=query,
                top_k=3
            )
        )

        if not retrieved_context:
            return {
                "agent": "RAGAgent",
                "query": query,
                "documents_used": [],
                "retrieved_context": [],
                "analysis": (
                    "No relevant project documentation "
                    "was found for this Pull Request."
                ),
                "context_found": False
            }

        documentation_text = json.dumps(
            retrieved_context,
            indent=2,
            ensure_ascii=False
        )

        prompt = self._build_prompt(
            title=title,
            description=description,
            diff=diff,
            documentation_text=documentation_text
        )

        analysis = self.llm_service.generate_review(
            prompt
        )

        documents_used = sorted({
            context["source"]
            for context in retrieved_context
        })

        return {
            "agent": "RAGAgent",
            "query": query,
            "documents_used": documents_used,
            "retrieved_context": retrieved_context,
            "analysis": analysis,
            "context_found": True
        }

    @staticmethod
    def _build_query(
        title: str,
        description: str,
        diff: str
    ) -> str:

        added_code_lines = []

        for line in diff.splitlines():
            if not line.startswith("+"):
                continue

            if line.startswith("+++"):
                continue

            clean_line = line[1:].strip()

            if clean_line:
                added_code_lines.append(
                    clean_line
                )

        added_code = "\n".join(
            added_code_lines
        )

        return (
            f"Pull Request title:\n{title}\n\n"
            f"Pull Request description:\n"
            f"{description}\n\n"
            f"Added code:\n{added_code}"
        )

    @staticmethod
    def _build_prompt(
        title: str,
        description: str,
        diff: str,
        documentation_text: str
    ) -> str:

        return f"""
You are RAGAgent, a specialized agent that interprets
project documentation for Pull Request reviews.

Your task is not to generate the final Bitbucket comment.

Analyze whether the retrieved documentation contains rules,
guidelines or constraints relevant to the Pull Request.

Only use information included in the retrieved documentation.
Do not invent project rules.

Explain:

- Which documentation is relevant.
- Which project rule may be violated.
- Why the rule applies to the changed code.
- What the AgentOrchestrator should consider in the final review.
- Whether the documentation provides enough evidence.

Pull Request title:
{title}

Pull Request description:
{description}

Pull Request diff:
{diff}

Retrieved project documentation:
{documentation_text}

Return a concise technical analysis for AgentOrchestrator.
"""