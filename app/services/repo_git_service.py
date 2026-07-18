import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class RepoGitService:

    def __init__(self):
        repository_path = os.getenv(
            "BITBUCKET_LOCAL_REPOSITORY_PATH"
        )

        if not repository_path:
            raise ValueError(
                "Missing BITBUCKET_LOCAL_REPOSITORY_PATH"
            )

        self.repository_path = Path(repository_path)

        if not self.repository_path.exists():
            raise ValueError(
                f"Repository path does not exist: "
                f"{self.repository_path}"
            )

    def get_file_content(self, relative_path: str) -> str:
        file_path = self.repository_path / relative_path

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {relative_path}"
            )

        return file_path.read_text(
            encoding="utf-8"
        )

    def list_python_files(self) -> list[str]:
        python_files = []

        for file_path in self.repository_path.rglob("*.py"):
            relative_path = file_path.relative_to(
                self.repository_path
            )

            python_files.append(str(relative_path))

        return python_files