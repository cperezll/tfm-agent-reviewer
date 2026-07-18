from app.services.repo_git_service import RepoGitService


def main():
    service = RepoGitService()

    files = service.list_python_files()

    print("RepoGitService execution successful")
    print("Python files:")

    for file_path in files:
        print(f"- {file_path}")

    file_content = service.get_file_content(
        "src/user_service.py"
    )

    print("\nContent of src/user_service.py:")
    print(file_content)


if __name__ == "__main__":
    main()