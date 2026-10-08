def split_tickets(tickets):
    """
    Split development tickets between Developer A and Developer B.

    Tickets are expected to be separated by Markdown headings
    starting with '## TKT-'.
    """

    sections = []
    current = []

    for line in tickets.splitlines():
        if line.startswith("## TKT-"):
            if current:
                sections.append("\n".join(current))

            current = [line]
        else:
            current.append(line)

    if current:
        sections.append("\n".join(current))

    # Remove empty sections
    sections = [
        section.strip()
        for section in sections
        if section.strip()
    ]

    developer_a = []
    developer_b = []

    for index, ticket in enumerate(sections):
        if index % 2 == 0:
            developer_a.append(ticket)
        else:
            developer_b.append(ticket)

    return developer_a, developer_b