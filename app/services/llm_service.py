import json
import os

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


class LLMService:

    def __init__(self):
        load_dotenv(override=True)

        base_url = os.getenv("AZURE_OPENAI_BASE_URL")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        if not base_url:
            raise ValueError(
                "AZURE_OPENAI_BASE_URL is not configured"
            )

        if not api_key:
            raise ValueError(
                "AZURE_OPENAI_API_KEY is not configured"
            )

        if not deployment:
            raise ValueError(
                "AZURE_OPENAI_DEPLOYMENT is not configured"
            )

        self.deployment = deployment

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def generate_review(
        self,
        prompt: str
    ) -> str:

        try:
            response = self.client.responses.create(
                model=self.deployment,
                input=prompt,
                reasoning={
                    "effort": "minimal"
                },
                text={
                    "verbosity": "low"
                },
                max_output_tokens=4000,
                store=False
            )

            review = response.output_text.strip()

            if not review:
                response_status = getattr(
                    response,
                    "status",
                    "unknown"
                )

                incomplete_details = getattr(
                    response,
                    "incomplete_details",
                    None
                )

                raise RuntimeError(
                    "Azure OpenAI returned an empty review. "
                    f"Response status: {response_status}. "
                    f"Incomplete details: {incomplete_details}"
                )

            return review

        except OpenAIError as error:
            raise RuntimeError(
                f"Azure OpenAI request failed: {error}"
            ) from error

    def generate_structured_review(
        self,
        prompt: str
    ) -> dict:

        try:
            response = self.client.responses.create(
                model=self.deployment,
                input=prompt,
                reasoning={
                    "effort": "minimal"
                },
                text={
                    "verbosity": "low",
                    "format": {
                        "type": "json_schema",
                        "name": "pull_request_review",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "summary": {
                                    "type": "string"
                                },
                                "findings": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "file": {
                                                "type": "string"
                                            },
                                            "line": {
                                                "type": "integer"
                                            },
                                            "code": {
                                                "type": "string"
                                            },
                                            "severity": {
                                                "type": "string",
                                                "enum": [
                                                    "High",
                                                    "Medium",
                                                    "Low"
                                                ]
                                            },
                                            "problem": {
                                                "type": "string"
                                            },
                                            "recommended_change": {
                                                "type": "string"
                                            }
                                        },
                                        "required": [
                                            "file",
                                            "line",
                                            "code",
                                            "severity",
                                            "problem",
                                            "recommended_change"
                                        ],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": [
                                "summary",
                                "findings"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                max_output_tokens=4000,
                store=False
            )

            review_text = response.output_text.strip()

            if not review_text:
                response_status = getattr(
                    response,
                    "status",
                    "unknown"
                )

                incomplete_details = getattr(
                    response,
                    "incomplete_details",
                    None
                )

                raise RuntimeError(
                    "Azure OpenAI returned an empty "
                    "structured review. "
                    f"Response status: {response_status}. "
                    f"Incomplete details: {incomplete_details}"
                )

            return json.loads(review_text)

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Azure OpenAI returned invalid JSON"
            ) from error

        except OpenAIError as error:
            raise RuntimeError(
                f"Azure OpenAI request failed: {error}"
            ) from error