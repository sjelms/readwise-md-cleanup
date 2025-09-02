import sys
import re
from pathlib import Path

def clean_markdown_highlights(file_path):
    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File not found — {file_path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Preserve YAML front matter
    cleaned_lines = []
    in_yaml = False
    highlight_buffer = []
    indent_sub_bullets = ("- Tags:", "- Note:")
    inside_bullet = False

    for line in lines:
        stripped = line.strip()

        # Handle YAML block
        if stripped == "---":
            in_yaml = not in_yaml
            cleaned_lines.append(line)
            continue
        if in_yaml:
            cleaned_lines.append(line)
            continue

        # Preserve headings, images, and other non-highlight markdown elements
        if stripped.startswith(("#", "!", "[", "*")):
            if highlight_buffer:
                combined = " ".join([l.strip() for l in highlight_buffer])
                cleaned_lines.append(f"- {combined}\n")
                highlight_buffer = []
            cleaned_lines.append(line)
            continue

        # Preserve Obsidian-style blockquotes and callouts
        if stripped.startswith(">"):
            if highlight_buffer:
                combined = " ".join([l.strip() for l in highlight_buffer])
                cleaned_lines.append(f"- {combined}\n")
                highlight_buffer = []
            cleaned_lines.append(line)
            continue

        # If the line starts a new bullet, flush previous buffer
        if stripped.startswith("- ") and not any(stripped.startswith(sub) for sub in indent_sub_bullets):
            if highlight_buffer:
                combined = " ".join([l.strip() for l in highlight_buffer])
                cleaned_lines.append(f"- {combined}\n")
                highlight_buffer = []

            highlight_buffer.append(stripped[2:])  # remove '- '

        elif any(stripped.startswith(sub) for sub in indent_sub_bullets):
            if highlight_buffer:
                combined = " ".join([l.strip() for l in highlight_buffer])
                cleaned_lines.append(f"- {combined}\n")
                highlight_buffer = []
            cleaned_lines.append(line)

        elif stripped == "":
            if highlight_buffer:
                combined = " ".join([l.strip() for l in highlight_buffer])
                cleaned_lines.append(f"- {combined}\n")
                highlight_buffer = []
            cleaned_lines.append(line)

        else:
            highlight_buffer.append(stripped)

    # Flush any remaining buffer
    if highlight_buffer:
        combined = " ".join([l.strip() for l in highlight_buffer])
        cleaned_lines.append(f"- {combined}\n")

    # Write back to the file
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

    print(f"✅ Cleaned: {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clean_highlights.py path/to/file.md")
    else:
        clean_markdown_highlights(sys.argv[1])
