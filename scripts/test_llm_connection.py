from app.services.llm_service import LLMService


def main():
    llm_service = LLMService()

    prompt = """
Review the following Python code.

Identify only relevant problems and explain them briefly.

def create_user(username, password):
    return {
        "username": username,
        "password": password,
        "active": True
    }
"""

    review = llm_service.generate_review(prompt)

    print("Azure OpenAI connection successful")
    print("----------------------------------")
    print(review)


if __name__ == "__main__":
    main()