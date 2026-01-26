"""Markdown parsing utilities using markdown-it-py."""

from markdown_it import MarkdownIt


def parse_sections(text: str) -> tuple[list[str], dict[str, list[str]]]:
    """Parse markdown text into general section and named sections.

    Returns:
        Tuple of (general_lines, sections_dict) where:
        - general_lines: Lines before the first H2 header
        - sections_dict: Dict mapping section names to their content lines (including header)
    """
    md = MarkdownIt()
    tokens = md.parse(text)
    lines = text.splitlines(keepends=True)

    # Find all H2 headers
    section_starts = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            # Get the content of the header
            # The next token is usually inline, which contains the text
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                header_content = tokens[i + 1].content.strip()
                # token.map contains [start_line, end_line] (0-based)
                start_line = token.map[0]
                section_starts.append((start_line, header_content))

    if not section_starts:
        return lines, {}

    # Extract general content (everything before first H2)
    first_section_start = section_starts[0][0]
    general_lines = lines[:first_section_start]

    # Extract named sections
    sections = {}
    for i, (start_line, header_name) in enumerate(section_starts):
        # End line is the start of the next section, or end of file
        if i + 1 < len(section_starts):
            end_line = section_starts[i + 1][0]
        else:
            end_line = len(lines)

        # Extract all lines for this section
        section_content = lines[start_line:end_line]
        sections[header_name] = section_content

    return general_lines, sections
