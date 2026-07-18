from app.orchestrator.agent_orchestrator import (
    AgentOrchestrator
)


def print_agent_decision(
    agent_name: str,
    decision: dict
):
    print(
        f"{agent_name} selected: "
        f'{decision["selected"]}'
    )

    reasons = decision["reasons"]

    if not reasons:
        print("- No additional context required")
        return

    for reason in reasons:
        print(f"- {reason}")


def print_selection(
    test_name: str,
    selection: dict
):
    print()
    print(test_name)
    print("-" * len(test_name))

    print_agent_decision(
        "RepoGitAgent",
        selection["RepoGitAgent"]
    )

    print_agent_decision(
        "RAGAgent",
        selection["RAGAgent"]
    )


def main():
    documentation_context = {
        "title": "Update README text",
        "description": (
            "Fix a general project description"
        )
    }

    documentation_lines = [
        {
            "file": "README.md",
            "line": 10,
            "code": (
                "Updated project description."
            )
        }
    ]

    functional_code_context = {
        "title": "Add calculation function",
        "description": (
            "Add a function that calculates a total"
        )
    }

    functional_code_lines = [
        {
            "file": "src/calculator.py",
            "line": 5,
            "code": (
                "def calculate_total(items):"
            )
        },
        {
            "file": "src/calculator.py",
            "line": 6,
            "code": (
                "return sum(items)"
            )
        }
    ]

    security_context = {
        "title": "Add user creation",
        "description": (
            "Create users with username, "
            "email and password"
        )
    }

    security_lines = [
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
            "code": (
                '"password": password,'
            )
        }
    ]

    documentation_selection = (
        AgentOrchestrator
        .select_context_agents(
            documentation_context,
            documentation_lines
        )
    )

    functional_selection = (
        AgentOrchestrator
        .select_context_agents(
            functional_code_context,
            functional_code_lines
        )
    )

    security_selection = (
        AgentOrchestrator
        .select_context_agents(
            security_context,
            security_lines
        )
    )

    print(
        "Dynamic agent selection test successful"
    )

    print_selection(
        "Simple documentation change",
        documentation_selection
    )

    print_selection(
        "Functional code change",
        functional_selection
    )

    print_selection(
        "Security-sensitive code change",
        security_selection
    )


if __name__ == "__main__":
    main()