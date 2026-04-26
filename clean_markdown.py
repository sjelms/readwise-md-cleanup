import argparse
import re
from pathlib import Path
from typing import cast


LIST_ITEM_RE = re.compile(r"^(\s*)((?:[-+*]|\d+[.)])(?:\s+\[[ xX]\])?)\s+(.*)$")
SETEXT_HEADING_RE = re.compile(r"^\s*(=+|-{3,})\s*$")
HORIZONTAL_RULE_RE = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$")
INLINE_FOOTNOTE_RE = re.compile(r"\.(\d+)(?=[\s\)\]\"'”’.,;:!?|]|$)")
TRAILING_INLINE_FOOTNOTE_RE = re.compile(
    r"(?<=[\)\]\"'”’*])\s+(\d+)(?=(?:\s{2,})?(?:\||$))"
)
ORDERED_PREFIX_RE = re.compile(r"^\d+[.)]")
REFERENCE_ENTRY_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*\S)\s*$")
UNNECESSARY_ESCAPE_RE = re.compile(r"\\([\[\]\(\)\.\-])")
HEADING_DECORATION_RE = re.compile(r"^[*_`~]+|[*_`~]+$")
INLINE_METADATA_TOKEN_RE = re.compile(r"(\[[A-Za-z][^\]]*:\s*[^\]]+\])(?=\S)")
BULLET_LABEL_RE = re.compile(r"^([A-Za-z][A-Za-z ]{0,50}:)\s*(\S.*)?$")
REFERENCE_HEADINGS = {
    "references",
    "works cited",
    "bibliography",
    "sources",
    "notes",
}


def normalize_text(text: str) -> str:
    return text.replace("\\'", "'").replace('\\"', '"')


def is_fence_delimiter(stripped: str) -> bool:
    return stripped.startswith("```") or stripped.startswith("~~~")


def is_verbatim_line(raw_line: str, stripped: str) -> bool:
    if not stripped:
        return False
    if stripped.startswith((">", "#", "![", "[^", "<")):
        return True
    if stripped.startswith("|") or stripped.endswith("|"):
        return True
    if HORIZONTAL_RULE_RE.match(stripped) or SETEXT_HEADING_RE.match(stripped):
        return True
    return bool(re.match(r"^(?:[*_]{1,3}|`{1,2}).*", stripped)) and raw_line == stripped + "\n"


def flush_paragraph(cleaned_lines: list[str], paragraph_buffer: list[str]) -> None:
    if not paragraph_buffer:
        return
    combined = " ".join(line.strip() for line in paragraph_buffer if line.strip())
    cleaned_lines.append(f"{normalize_text(combined)}\n")
    paragraph_buffer.clear()


def flush_list_item(cleaned_lines: list[str], list_state: dict | None) -> None:
    if not list_state:
        return
    lines = cast(list[str], list_state["lines"])
    combined = " ".join(line.strip() for line in lines if line.strip())
    prefix = str(list_state["prefix"])
    if prefix in {"-", "+", "*"}:
        match = BULLET_LABEL_RE.match(combined)
        if match and not match.group(1).strip().startswith("**"):
            label = match.group(1).strip()
            remainder = (match.group(2) or "").strip()
            combined = f"**{label}** {remainder}" if remainder else f"**{label}**"

    cleaned_lines.append(f"{list_state['indent']}{prefix} {normalize_text(combined)}\n")
    list_state.clear()


def is_terminal_wrapped_bullet(indent: str, prefix: str) -> bool:
    # Terminal copies often prefix top-level bullets with three spaces and "*".
    return prefix == "*" and len(indent.expandtabs(4)) >= 3


def is_terminal_wrapped_ordered_item(indent: str, prefix: str) -> bool:
    return is_ordered_prefix(prefix) and len(indent.expandtabs(4)) >= 2


def is_ordered_prefix(prefix: str) -> bool:
    return bool(ORDERED_PREFIX_RE.match(prefix))


def collapse_blank_lines_between_list_items(lines: list[str]) -> list[str]:
    collapsed: list[str] = []
    for index, line in enumerate(lines):
        if line.strip() == "":
            prev_line = collapsed[-1] if collapsed else ""
            next_line = lines[index + 1] if index + 1 < len(lines) else ""
            if LIST_ITEM_RE.match(prev_line) and LIST_ITEM_RE.match(next_line):
                continue
        collapsed.append(line)
    return collapsed


def format_inline_footnotes(line: str) -> str:
    if line.lstrip().startswith("[^"):
        return line

    def replacer(match: re.Match[str]) -> str:
        if match.start() > 0 and line[match.start() - 1].isdigit():
            return match.group(0)
        return f".[^{match.group(1)}]"

    line = INLINE_FOOTNOTE_RE.sub(replacer, line)
    return TRAILING_INLINE_FOOTNOTE_RE.sub(r" [^\1]", line)


def remove_unnecessary_escapes(line: str) -> str:
    return UNNECESSARY_ESCAPE_RE.sub(r"\1", line)


def cleanup_body_line(line: str) -> str:
    line = format_inline_footnotes(remove_unnecessary_escapes(line))
    return INLINE_METADATA_TOKEN_RE.sub(r"\1 ", line)


def is_soft_wrap_continuation_candidate(raw_line: str) -> bool:
    stripped = raw_line.strip()
    if not stripped:
        return False
    # Two-space indents often come from copied hard wraps and are not code blocks.
    if len(raw_line) - len(raw_line.lstrip(" \t")) < 2:
        return False
    if raw_line.startswith(("    ", "\t")):
        return False
    if LIST_ITEM_RE.match(raw_line):
        return False
    return not is_verbatim_line(raw_line, stripped)


def normalize_heading_text(stripped: str) -> str:
    heading_text = stripped.lstrip("#").strip().lower()
    while True:
        updated = HEADING_DECORATION_RE.sub("", heading_text).strip()
        if updated == heading_text:
            return updated
        heading_text = updated


def is_reference_heading(stripped: str) -> bool:
    return normalize_heading_text(stripped) in REFERENCE_HEADINGS


def find_trailing_reference_entries(lines: list[str]) -> set[int]:
    trailing_indices: set[int] = set()
    entry_count = 0
    index = len(lines) - 1

    while index >= 0 and lines[index].strip() == "":
        index -= 1

    while index >= 0:
        stripped = lines[index].strip()
        if stripped == "":
            trailing_indices.add(index)
            index -= 1
            continue

        if REFERENCE_ENTRY_RE.match(lines[index]):
            trailing_indices.add(index)
            entry_count += 1
            index -= 1
            continue

        break

    if entry_count < 2:
        return set()

    return {
        line_index for line_index in trailing_indices if REFERENCE_ENTRY_RE.match(lines[line_index])
    }


def apply_footnote_formatting(lines: list[str]) -> list[str]:
    formatted_lines: list[str] = []
    in_yaml = bool(lines) and lines[0].strip() == "---"
    in_fence = False
    in_reference_section = False
    trailing_reference_entries = find_trailing_reference_entries(lines)

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()

        if in_yaml:
            formatted_lines.append(raw_line)
            if index != 0 and stripped == "---":
                in_yaml = False
            continue

        if in_fence:
            formatted_lines.append(raw_line)
            if is_fence_delimiter(stripped):
                in_fence = False
            continue

        if is_fence_delimiter(stripped):
            formatted_lines.append(raw_line)
            in_fence = True
            continue

        if stripped.startswith("#"):
            in_reference_section = is_reference_heading(stripped)
            formatted_lines.append(raw_line)
            continue

        if normalize_heading_text(stripped) in REFERENCE_HEADINGS:
            in_reference_section = True
            formatted_lines.append(raw_line)
            continue

        reference_match = REFERENCE_ENTRY_RE.match(raw_line)
        if in_reference_section:
            if stripped and SETEXT_HEADING_RE.match(stripped):
                formatted_lines.append(raw_line)
                continue

            if reference_match:
                indent, number, text = reference_match.groups()
                formatted_lines.append(f"{indent}[^{number}]: {text}\n")
                continue

        if index in trailing_reference_entries and reference_match:
            indent, number, text = reference_match.groups()
            formatted_lines.append(f"{indent}[^{number}]: {text}\n")
            continue

        formatted_lines.append(cleanup_body_line(raw_line))

    return formatted_lines


def clean_markdown_file(file_path: str | Path) -> bool:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    original = path.read_text(encoding="utf-8")
    lines = original.splitlines(keepends=True)

    cleaned_lines: list[str] = []
    paragraph_buffer: list[str] = []
    list_state: dict[str, object] = {}
    in_yaml = bool(lines) and lines[0].strip() == "---"
    in_fence = False
    ordered_context_active = False

    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()

        if in_yaml:
            cleaned_lines.append(raw_line)
            if index != 0 and stripped == "---":
                in_yaml = False
            continue

        if in_fence:
            cleaned_lines.append(raw_line)
            if is_fence_delimiter(stripped):
                in_fence = False
            continue

        if is_fence_delimiter(stripped):
            flush_list_item(cleaned_lines, list_state or None)
            flush_paragraph(cleaned_lines, paragraph_buffer)
            cleaned_lines.append(raw_line)
            in_fence = True
            continue

        if stripped == "":
            next_index = index + 1
            if paragraph_buffer and next_index < len(lines):
                next_raw_line = lines[next_index]
                if is_soft_wrap_continuation_candidate(next_raw_line):
                    continue
            flush_list_item(cleaned_lines, list_state or None)
            flush_paragraph(cleaned_lines, paragraph_buffer)
            cleaned_lines.append(raw_line)
            ordered_context_active = False
            continue

        list_match = LIST_ITEM_RE.match(raw_line)
        if list_match:
            previous_was_ordered = bool(
                list_state and is_ordered_prefix(cast(str, list_state.get("prefix", "")))
            )
            flush_list_item(cleaned_lines, list_state or None)
            flush_paragraph(cleaned_lines, paragraph_buffer)
            indent = list_match.group(1)
            prefix = list_match.group(2)
            current_is_ordered = is_ordered_prefix(prefix)
            if current_is_ordered:
                ordered_context_active = True
            spaced = is_terminal_wrapped_bullet(indent, prefix)
            if spaced:
                indent = "\t" if previous_was_ordered or ordered_context_active else ""
                prefix = "-"
            elif is_terminal_wrapped_ordered_item(indent, prefix):
                indent = ""

            if prefix in {"-", "+", "*"} and ordered_context_active:
                indent = "\t"

            list_state["indent"] = indent
            list_state["prefix"] = prefix
            list_state["lines"] = [list_match.group(3)]
            list_state["spaced"] = spaced
            continue

        if is_verbatim_line(raw_line, stripped) or (
            raw_line.startswith(("    ", "\t")) and not paragraph_buffer and not list_state
        ):
            flush_list_item(cleaned_lines, list_state or None)
            flush_paragraph(cleaned_lines, paragraph_buffer)
            cleaned_lines.append(raw_line)
            continue

        if list_state:
            cast(list[str], list_state["lines"]).append(stripped)
            continue

        ordered_context_active = False
        paragraph_buffer.append(stripped)

    flush_list_item(cleaned_lines, list_state or None)
    flush_paragraph(cleaned_lines, paragraph_buffer)

    cleaned = "".join(apply_footnote_formatting(collapse_blank_lines_between_list_items(cleaned_lines)))
    if cleaned != original:
        path.write_text(cleaned, encoding="utf-8")
        return True
    return False


def iter_markdown_files(paths: list[str]) -> list[Path]:
    markdown_files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file():
            markdown_files.append(path)
            continue
        if path.is_dir():
            markdown_files.extend(sorted(path.rglob("*.md")))
            continue
        raise FileNotFoundError(f"Path not found: {raw_path}")
    return markdown_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize soft-wrapped markdown paragraphs and list items in place."
    )
    parser.add_argument("paths", nargs="+", help="Markdown file(s) or directories to clean.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    changed_files = 0
    for path in iter_markdown_files(args.paths):
        if clean_markdown_file(path):
            changed_files += 1
            print(f"Cleaned: {path}")
        else:
            print(f"Unchanged: {path}")

    return 0 if changed_files >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
