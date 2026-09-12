"""Markdown parsing utilities using markdown-it-py."""

import fnmatch
from collections.abc import Sequence
from typing import NamedTuple

from markdown_it import MarkdownIt


class SectionData(NamedTuple):
    """Data for a parsed section."""

    content: list[str]
    glob_pattern: str | None


def extract_glob_directive(
    content_lines: list[str],
) -> tuple[list[str], str | None]:
    """Extract glob directive from section content if present.

    Checks the first non-empty line after the header for 'globs: PATTERN'.

    Args:
        content_lines: Lines including the header

    Returns:
        Tuple of (content_without_directive, glob_pattern)
        - glob_pattern is None if no directive found (means alwaysApply)
        - glob_pattern is "manual" for manual-only sections
    """
    if not content_lines:
        return content_lines, None

    header_idx = None
    for i, line in enumerate(content_lines):
        if line.startswith("## "):
            header_idx = i
            break

    if header_idx is None:
        return content_lines, None

    for i in range(header_idx + 1, len(content_lines)):
        line = content_lines[i].strip()
        if not line:
            continue

        if line.lower().startswith("globs:"):
            glob_value = line[6:].strip()
            filtered_content = content_lines[:i] + content_lines[i + 1 :]
            return filtered_content, glob_value

        break

    return content_lines, None


def parse_sections(text: str) -> tuple[list[str], dict[str, SectionData]]:
    """Parse markdown text into general section and named sections.

    Returns:
        Tuple of (general_lines, sections_dict) where:
        - general_lines: Lines before the first H2 header
        - sections_dict: Dict mapping section names to SectionData (content + glob_pattern)
    """
    md = MarkdownIt()
    tokens = md.parse(text)
    lines = text.splitlines(keepends=True)

    # Find all H2 headers
    section_starts = []
    for i, token in enumerate(tokens):
        # Get the content of the header
        # The next token is usually inline, which contains the text
        if (
            token.type == "heading_open"
            and token.tag == "h2"
            and i + 1 < len(tokens)
            and tokens[i + 1].type == "inline"
        ):
            header_content = tokens[i + 1].content.strip()
            # token.map contains [start_line, end_line] (0-based)
            if token.map:
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

        # Extract glob directive if present
        filtered_content, glob_pattern = extract_glob_directive(section_content)

        sections[header_name] = SectionData(
            content=filtered_content, glob_pattern=glob_pattern
        )

    return general_lines, sections


def filter_markdown_by_globs(
    text: str,
    exclude_globs: Sequence[str] | None = None,
    include_globs: Sequence[str] | None = None,
) -> tuple[str, list[str]]:
    """Filter markdown sections based on exclude and include glob patterns."""
    exclude_patterns = (
        [p.strip() for raw in exclude_globs for p in raw.split(",") if p.strip()]
        if exclude_globs
        else []
    )
    include_patterns = (
        [p.strip() for raw in include_globs for p in raw.split(",") if p.strip()]
        if include_globs
        else []
    )

    if not exclude_patterns and not include_patterns:
        return text, []

    include_has_wildcard = any(
        pat in ("*", "**/*", "**") for pat in include_patterns
    )
    # patterns for matching section globs (bare '*' designates unglobbed sections)
    glob_include_patterns = [p for p in include_patterns if p != "*"]

    md = MarkdownIt()
    tokens = md.parse(text)
    lines = text.splitlines(keepends=True)

    # find all H2 headers
    section_starts = []
    for i, token in enumerate(tokens):
        if (
            token.type == "heading_open"
            and token.tag == "h2"
            and i + 1 < len(tokens)
            and tokens[i + 1].type == "inline"
        ):
            header_content = tokens[i + 1].content.strip()
            if token.map:
                section_starts.append((token.map[0], header_content))

    if not section_starts:
        return text, []

    first_section_start = section_starts[0][0]
    result_lines = list(lines[:first_section_start])
    omitted_headers: list[str] = []

    for i, (start_line, header_name) in enumerate(section_starts):
        end_line = (
            section_starts[i + 1][0] if i + 1 < len(section_starts) else len(lines)
        )
        section_content = lines[start_line:end_line]
        _, glob_pattern = extract_glob_directive(section_content)

        if glob_pattern is None:
            # unglobbed sections are omitted under include globs unless wildcard is present
            if include_patterns and not include_has_wildcard:
                omitted_headers.append(header_name)
                continue

            result_lines.extend(section_content)
            continue

        section_globs = [g.strip() for g in glob_pattern.split(",") if g.strip()]
        if not section_globs:
            # empty glob directive behaves like an unglobbed section
            if include_patterns and not include_has_wildcard:
                omitted_headers.append(header_name)
                continue

            result_lines.extend(section_content)
            continue

        # section must match at least one include pattern when include patterns are active
        if glob_include_patterns:
            matches_include = any(
                fnmatch.fnmatch(sg, pat) or fnmatch.fnmatch(pat, sg)
                for pat in glob_include_patterns
                for sg in section_globs
            )
            if not matches_include:
                omitted_headers.append(header_name)
                continue


        # all globs in section must match an exclude pattern for section to be omitted
        if exclude_patterns:
            all_matched = all(
                any(fnmatch.fnmatch(sg, pat) for pat in exclude_patterns)
                for sg in section_globs
            )
            if all_matched:
                omitted_headers.append(header_name)
                continue

        result_lines.extend(section_content)

    return "".join(result_lines), omitted_headers

