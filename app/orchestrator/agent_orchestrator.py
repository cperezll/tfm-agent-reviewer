import hashlib
import json

from app.agents.bitbucket_agent import BitbucketAgent
from app.agents.repo_git_agent import RepoGitAgent
from app.services.bitbucket_service import BitbucketService
from app.services.diff_service import DiffService
from app.services.llm_service import LLMService


class AgentOrchestrator:

    def __init__(self):
        self.bitbucket_agent = BitbucketAgent()
        self.repo_git_agent = RepoGitAgent()
        self.bitbucket_service = BitbucketService()
        self.diff_service = DiffService()
        self.llm_service = LLMService()

    def review_pull_request(
        self,
        pull_request_id: int
    ) -> dict:

        selected_agents = [
            "BitbucketAgent"
        ]

        bitbucket_context = self.bitbucket_agent.execute(
            pull_request_id
        )

        collected_context = {
            "bitbucket": bitbucket_context
        }

        diff = bitbucket_context["diff"]

        added_lines = self.diff_service.extract_added_lines(
            diff
        )

        review_id = self._build_review_id(diff)

        summary_marker = (
            "<!-- tfm-agent-reviewer:"
            f"summary:{review_id} -->"
        )

        existing_comments = (
            self.bitbucket_service
            .get_pull_request_comments(
                pull_request_id
            )
        )

        existing_summary = self._find_comment_by_marker(
            existing_comments,
            summary_marker
        )

        # If the same diff has already been completely
        # reviewed, stop before calling any LLM.
        if existing_summary:
            return {
                "orchestrator": "AgentOrchestrator",
                "pull_request_id": pull_request_id,
                "selected_agents": selected_agents,
                "context": collected_context,
                "review": None,
                "published_inline_comments": [],
                "published_tasks": [],
                "published_summary_comment": {
                    "id": existing_summary.get("id"),
                    "action": "reused",
                    "url": (
                        existing_summary
                        .get("links", {})
                        .get("html", {})
                        .get("href")
                    )
                },
                "deduplication": {
                    "review_id": review_id,
                    "reason": (
                        "The same Pull Request diff "
                        "was already reviewed"
                    )
                },
                "review_status": (
                    "review_already_published"
                )
            }

        existing_tasks = (
            self.bitbucket_service
            .get_pull_request_tasks(
                pull_request_id
            )
        )

        repo_git_context = self.repo_git_agent.execute(
            bitbucket_context
        )

        selected_agents.append(
            "RepoGitAgent"
        )

        collected_context["repo_git"] = (
            repo_git_context
        )

        prompt = self._build_review_prompt(
            collected_context,
            added_lines
        )

        structured_review = (
            self.llm_service
            .generate_structured_review(
                prompt
            )
        )

        valid_findings, discarded_findings = (
            self._validate_findings(
                structured_review.get(
                    "findings",
                    []
                ),
                added_lines
            )
        )

        published_inline_comments = []
        published_tasks = []

        inline_comments_created = 0
        inline_comments_reused = 0
        tasks_created = 0
        tasks_reused = 0

        for finding in valid_findings:
            finding_marker = (
                self._build_finding_marker(
                    review_id,
                    finding
                )
            )

            existing_comment = (
                self._find_comment_by_marker(
                    existing_comments,
                    finding_marker
                )
            )

            if existing_comment:
                published_comment = existing_comment
                comment_action = "reused"
                inline_comments_reused += 1

            else:
                inline_content = (
                    self._build_inline_comment(
                        finding,
                        finding_marker
                    )
                )

                published_comment = (
                    self.bitbucket_service
                    .post_pull_request_inline_comment(
                        pull_request_id=(
                            pull_request_id
                        ),
                        file_path=finding["file"],
                        line_number=finding["line"],
                        comment=inline_content
                    )
                )

                existing_comments.append(
                    published_comment
                )

                comment_action = "created"
                inline_comments_created += 1

            comment_id = published_comment.get("id")

            if not comment_id:
                raise RuntimeError(
                    "Bitbucket did not return the ID "
                    "of the inline comment"
                )

            published_inline_comments.append({
                "id": comment_id,
                "file": finding["file"],
                "line": finding["line"],
                "severity": finding["severity"],
                "action": comment_action,
                "url": (
                    published_comment
                    .get("links", {})
                    .get("html", {})
                    .get("href")
                )
            })

            if finding["severity"] == "High":
                existing_task = (
                    self._find_task_by_comment_id(
                        existing_tasks,
                        comment_id
                    )
                )

                if existing_task:
                    published_task = existing_task
                    task_action = "reused"
                    tasks_reused += 1

                else:
                    task_content = (
                        "Fix this high-severity issue "
                        "before merging the Pull Request."
                        "\n\n"
                        f'Location: {finding["file"]}:'
                        f'{finding["line"]}\n\n'
                        f'Problem: {finding["problem"]}'
                        "\n\n"
                        "Recommended change: "
                        f'{finding["recommended_change"]}'
                    )

                    published_task = (
                        self.bitbucket_service
                        .create_pull_request_task(
                            pull_request_id=(
                                pull_request_id
                            ),
                            comment_id=comment_id,
                            task_content=task_content
                        )
                    )

                    existing_tasks.append(
                        published_task
                    )

                    task_action = "created"
                    tasks_created += 1

                published_tasks.append({
                    "id": published_task.get("id"),
                    "comment_id": comment_id,
                    "file": finding["file"],
                    "line": finding["line"],
                    "severity": finding["severity"],
                    "state": published_task.get(
                        "state"
                    ),
                    "action": task_action,
                    "url": (
                        published_task
                        .get("links", {})
                        .get("html", {})
                        .get("href")
                    )
                })

        summary_content = self._build_summary_comment(
            valid_findings
        )

        summary_content = (
            f"{summary_content}\n\n"
            f"{summary_marker}"
        )

        published_summary = (
            self.bitbucket_service
            .post_pull_request_comment(
                pull_request_id,
                summary_content
            )
        )

        return {
            "orchestrator": "AgentOrchestrator",
            "pull_request_id": pull_request_id,
            "selected_agents": selected_agents,
            "context": collected_context,
            "review": {
                "summary": summary_content,
                "findings": valid_findings
            },
            "published_inline_comments": (
                published_inline_comments
            ),
            "published_tasks": published_tasks,
            "published_summary_comment": {
                "id": published_summary.get("id"),
                "action": "created",
                "created_on": published_summary.get(
                    "created_on"
                ),
                "url": (
                    published_summary
                    .get("links", {})
                    .get("html", {})
                    .get("href")
                )
            },
            "deduplication": {
                "review_id": review_id,
                "inline_comments_created": (
                    inline_comments_created
                ),
                "inline_comments_reused": (
                    inline_comments_reused
                ),
                "tasks_created": tasks_created,
                "tasks_reused": tasks_reused
            },
            "discarded_findings_count": len(
                discarded_findings
            ),
            "review_status": "review_published"
        }

    def _build_review_id(
        self,
        diff: str
    ) -> str:

        diff_hash = hashlib.sha256(
            diff.encode("utf-8")
        ).hexdigest()

        return diff_hash[:16]

    def _build_finding_marker(
        self,
        review_id: str,
        finding: dict
    ) -> str:

        finding_content = (
            f'{review_id}|'
            f'{finding["file"]}|'
            f'{finding["line"]}|'
            f'{finding["code"]}'
        )

        finding_hash = hashlib.sha256(
            finding_content.encode("utf-8")
        ).hexdigest()[:16]

        return (
            "<!-- tfm-agent-reviewer:"
            f"finding:{finding_hash} -->"
        )

    def _find_comment_by_marker(
        self,
        comments: list[dict],
        marker: str
    ):

        for comment in comments:
            if comment.get("deleted"):
                continue

            raw_content = (
                comment
                .get("content", {})
                .get("raw", "")
            )

            if marker in raw_content:
                return comment

        return None

    def _find_task_by_comment_id(
        self,
        tasks: list[dict],
        comment_id: int
    ):

        for task in tasks:
            linked_comment_id = (
                task
                .get("comment", {})
                .get("id")
            )

            if linked_comment_id == comment_id:
                return task

        return None

    def _build_inline_comment(
        self,
        finding: dict,
        finding_marker: str
    ) -> str:

        return (
            f'### {finding["severity"]} severity\n\n'
            f'**Problem:** {finding["problem"]}\n\n'
            "**Recommended change:** "
            f'{finding["recommended_change"]}\n\n'
            f"{finding_marker}"
        )

    def _build_review_prompt(
        self,
        collected_context: dict,
        added_lines: list[dict]
    ) -> str:

        bitbucket_context = collected_context[
            "bitbucket"
        ]

        repo_git_context = collected_context.get(
            "repo_git",
            {}
        )

        repo_git_summary = repo_git_context.get(
            "summary",
            ""
        )

        repo_git_files_json = json.dumps(
            repo_git_context.get(
                "files_analyzed",
                []
            ),
            indent=2,
            ensure_ascii=False
        )

        repo_git_findings_json = json.dumps(
            repo_git_context.get(
                "findings",
                []
            ),
            indent=2,
            ensure_ascii=False
        )

        title = bitbucket_context["title"]

        description = bitbucket_context.get(
            "description",
            ""
        )

        source_branch = bitbucket_context[
            "source_branch"
        ]

        destination_branch = bitbucket_context[
            "destination_branch"
        ]

        diff = bitbucket_context["diff"]

        added_lines_json = json.dumps(
            added_lines,
            indent=2,
            ensure_ascii=False
        )

        return f"""
You are reviewing a Pull Request.

The complete diff is provided so that you can understand
the surrounding code and avoid false positives.

Report only relevant problems directly supported by the diff.

Prioritize:
- Security vulnerabilities
- Functional errors
- Clear maintainability problems

Do not report:
- Generic best practices
- Optional improvements
- Missing functionality that cannot be confirmed
- Style preferences unless they cause a real problem

For each finding:

- Select a location exclusively from the allowed added lines.
- Copy the file, line and code exactly as they appear.
- Anchor the finding to the most specific line that directly
  demonstrates the problem.
- Do not attach a finding to a function declaration when a more
  specific problematic line exists.
- Do not report missing braces, delimiters or syntax elements if
  they appear as unchanged context in the complete diff.
- Do not invent file names or line numbers.

Return a maximum of 3 relevant findings.

Pull Request title:
{title}

Pull Request description:
{description}

Source branch:
{source_branch}

Destination branch:
{destination_branch}

Specialized repository analysis:

Files analyzed by RepoGitAgent:
{repo_git_files_json}

RepoGitAgent summary:
{repo_git_summary}

RepoGitAgent findings:
{repo_git_findings_json}

Use the RepoGitAgent analysis only as supporting context.
Validate every final finding against the Pull Request diff.
Do not copy a RepoGitAgent finding if it is not directly
supported by the changed code.

Complete Pull Request diff:
{diff}

Allowed added lines:
{added_lines_json}
"""

    def _validate_findings(
        self,
        findings: list[dict],
        added_lines: list[dict]
    ) -> tuple[list[dict], list[dict]]:

        valid_locations = {
            (
                added_line["file"],
                added_line["line"],
                added_line["code"]
            )
            for added_line in added_lines
        }

        valid_findings = []
        discarded_findings = []

        for finding in findings:
            finding_location = (
                finding["file"],
                finding["line"],
                finding["code"]
            )

            if finding_location in valid_locations:
                valid_findings.append(finding)
            else:
                discarded_findings.append(finding)

        return valid_findings, discarded_findings

    def _build_summary_comment(
        self,
        findings: list[dict]
    ) -> str:

        if not findings:
            return (
                "## Automated Pull Request Review\n\n"
                "No relevant issues found."
            )

        high_count = 0
        medium_count = 0
        low_count = 0

        for finding in findings:
            severity = finding["severity"]

            if severity == "High":
                high_count += 1
            elif severity == "Medium":
                medium_count += 1
            elif severity == "Low":
                low_count += 1

        reviewer_attention_count = (
            medium_count + low_count
        )

        summary_lines = [
            "## Automated Pull Request Review",
            "",
            f"Detected **{len(findings)} relevant issue(s)**.",
            "",
            "### Severity summary",
            "",
            f"- High: {high_count}",
            f"- Medium: {medium_count}",
            f"- Low: {low_count}",
            "",
            "### Review actions",
            "",
            (
                "- Tasks associated with High findings: "
                f"{high_count}"
            ),
            (
                "- Findings for reviewer assessment: "
                f"{reviewer_attention_count}"
            ),
            "",
            "### Findings",
            ""
        ]

        for finding in findings:
            summary_lines.append(
                f'- **{finding["severity"]}** '
                f'`{finding["file"]}:'
                f'{finding["line"]}` — '
                f'{finding["problem"]}'
            )

        summary_lines.extend([
            "",
            "Detailed comments were added directly "
            "to the affected lines.",
            "",
            "High-severity findings were automatically "
            "converted into Pull Request tasks."
        ])

        return "\n".join(summary_lines)