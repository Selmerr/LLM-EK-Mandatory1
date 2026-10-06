import re


def parse_code_changes(response):
    """
    Parse code changes returned by the Developer agent.

    Expected format:

    FILE: path/to/file
    CONTENT:
    complete file contents
    END FILE
    """

    pattern = re.compile(
        r"FILE:\s*(.+?)\s*"
        r"CONTENT:\s*\n"
        r"(.*?)"
        r"\nEND FILE",
        re.DOTALL
    )

    matches = pattern.findall(response)

    changes = []

    for path, content in matches:
        changes.append({
            "path": path.strip(),
            "content": content
        })

    return changes