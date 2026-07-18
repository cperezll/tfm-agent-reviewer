from app.services.llm_service import LLMService
from app.services.repo_git_service import RepoGitService


class RepoGitAgent:

    def __init__(self):
        self.repo_git_service = RepoGitService()
        self.llm_service = LLMService()

    def execute(
        self,
        pull_request_context: dict
    ) -> dict:

        pull_request_diff = pull_request_context.get(
            "diff",
            ""
        )

        if not pull_request_diff:
            raise ValueError(
                "Pull Request diff is required"
            )

        python_files = (
            self.repo_git_service.list_python_files()
        )

        repository_context = []

        for file_path in python_files:
            file_content = (
                self.repo_git_service.get_file_content(
                    file_path
                )
            )

            repository_context.append(
                f"FILE: {file_path}\n"
                f"{file_content}"
            )

        repository_text = "\n\n".join(
            repository_context
        )

        prompt = f"""
You are RepoGitAgent, a specialized agent for repository
analysis.

Your task is to analyze the Pull Request diff together with
the current repository files.

Do not write the final Bitbucket comment. Return technical
findings that will be sent to AgentOrchestrator.

Focus on:
- Impact of the modified code.
- Related functions or files.
- Possible bugs or security risks.
- Missing validations.
- Problems that cannot be detected from the diff alone.

Pull Request title:
{pull_request_context.get("title", "")}

Pull Request description:
{pull_request_context.get("description", "")}

Pull Request diff:
{pull_request_diff}

Current repository context:
{repository_text}

Only report findings supported by the provided code.
"""

        analysis = (
            self.llm_service.generate_structured_review(
                prompt
            )
        )

        return {
            "agent": "RepoGitAgent",
            "files_analyzed": python_files,
            "summary": analysis["summary"],
            "findings": analysis["findings"]
        }