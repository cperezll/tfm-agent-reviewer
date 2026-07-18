from app.orchestrator.agent_orchestrator import (
    AgentOrchestrator
)


def print_selection(
    test_name: str,
    selection: dict
):
    print(f"\n{test_name}")
    print("-" * len(test_name))
    print(
        "RepoGitAgent selected: "
        f'{selection["RepoGitAgent"]["selected"]}'
    )

    print("Reasons:")

    reasons = selection["RepoGitAgent"]["reasons"]

    if not reasons:
        print("- No repository context required")
        return

    for reason in reasons:
        print(f"- {reason}")


def main():
    simple_documentation_context = {
        "title": "Update README text",
        "description": "Fix a documentation sentence"
    }

    simple_documentation_lines = [
        {
            "file": "README.md",
            "line": 10,
            "code": "Updated project description."
        }
    ]

    code_change_context = {
        "title": "Add user creation",
        "description": "Add a new user function"
    }

    code_change_lines = [
        {
            "file": "src/user_service.py",
            "line": 6,
            "code": (
                "def create_user("
                "username, password, email):"
            )
        },
        {
            "file": "src/user_service.py",
            "line": 9,
            "code": '"password": password,'
        }
    ]

    simple_selection = (
        AgentOrchestrator.select_context_agents(
            simple_documentation_context,
            simple_documentation_lines
        )
    )

    code_selection = (
        AgentOrchestrator.select_context_agents(
            code_change_context,
            code_change_lines
        )
    )

    print("Agent selection test successful")

    print_selection(
        "Simple documentation change",
        simple_selection
    )

    print_selection(
        "Code and sensitive data change",
        code_selection
    )


if __name__ == "__main__":
    main()