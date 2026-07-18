import json

from app.agents.bitbucket_agent import BitbucketAgent
from app.services.diff_service import DiffService
from app.services.llm_service import LLMService


def main():
    bitbucket_agent = BitbucketAgent()
    diff_service = DiffService()
    llm_service = LLMService()

    context = bitbucket_agent.execute(1)

    added_lines = diff_service.extract_added_lines(
        context["diff"]
    )

    added_lines_json = json.dumps(
        added_lines,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are reviewing a Pull Request.

The complete diff is provided so that you can understand
the surrounding code and avoid false positives.

Report only relevant problems directly supported by the diff.

For each finding:

- Select a location exclusively from the allowed added lines.
- Copy the file, line and code exactly as they appear.
- Anchor the finding to the most specific line that directly
  demonstrates the problem.
- Do not attach a finding to a function declaration when a more
  specific problematic line exists.
- Do not report missing braces, delimiters or syntax elements if
  they are present in the complete diff as unchanged context.
- Do not invent missing functionality or business requirements.

Return a maximum of 3 findings.

Pull Request title:
{context["title"]}

Pull Request description:
{context["description"]}

Complete Pull Request diff:
{context["diff"]}

Allowed added lines:
{added_lines_json}
"""

    review = llm_service.generate_structured_review(
        prompt
    )

    valid_added_lines = {
        (
            added_line["file"],
            added_line["line"],
            added_line["code"]
        )
        for added_line in added_lines
    }

    valid_findings = []
    invalid_findings = []

    for finding in review["findings"]:
        finding_location = (
            finding["file"],
            finding["line"],
            finding["code"]
        )

        if finding_location in valid_added_lines:
            valid_findings.append(finding)
        else:
            invalid_findings.append(finding)

    review["findings"] = valid_findings

    print("Structured review generated")
    print("---------------------------")
    print(
        json.dumps(
            review,
            indent=2,
            ensure_ascii=False
        )
    )

    if invalid_findings:
        print()
        print("Invalid findings discarded")
        print("--------------------------")
        print(
            json.dumps(
                invalid_findings,
                indent=2,
                ensure_ascii=False
            )
        )


if __name__ == "__main__":
    main()