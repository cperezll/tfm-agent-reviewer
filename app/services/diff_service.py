import re


class DiffService:

    def extract_added_lines(self, diff: str) -> list[dict]:
        added_lines = []

        current_file = None
        new_line_number = 0

        for line in diff.splitlines():

            if line.startswith("+++ b/"):
                current_file = line[6:]
                continue

            if line.startswith("@@"):
                match = re.search(
                    r"\+(\d+)(?:,\d+)?",
                    line
                )

                if match:
                    new_line_number = int(
                        match.group(1)
                    )

                continue

            if current_file is None:
                continue

            if line.startswith("+") and not line.startswith("+++"):
                added_lines.append({
                    "file": current_file,
                    "line": new_line_number,
                    "code": line[1:]
                })

                new_line_number += 1
                continue

            if line.startswith("-") and not line.startswith("---"):
                continue

            if not line.startswith("\\"):
                new_line_number += 1

        return added_lines  