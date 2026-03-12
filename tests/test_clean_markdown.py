import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from clean_markdown import clean_markdown_file


REPO_ROOT = Path(__file__).resolve().parents[1]


class CleanMarkdownTests(unittest.TestCase):
    def write_temp_markdown(self, content: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "sample.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_merges_wrapped_list_items_and_preserves_nested_lists(self) -> None:
        path = self.write_temp_markdown(
            "# Notes\n\n"
            "- first line\n"
            "continued line\n"
            "  - nested detail\n"
            "\n"
        )

        changed = clean_markdown_file(path)

        self.assertTrue(changed)
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# Notes\n\n- first line continued line\n  - nested detail\n\n",
        )

    def test_preserves_readwise_style_tag_and_note_sub_bullets(self) -> None:
        path = self.write_temp_markdown(
            "- wrapped highlight line one\n"
            "line two\n"
            "    - Tags: [[blue]]\n"
            "    - Note: Keep this note\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "- wrapped highlight line one line two\n"
            "    - Tags: [[blue]]\n"
            "    - Note: Keep this note\n",
        )

    def test_preserves_fenced_code_and_blockquotes(self) -> None:
        path = self.write_temp_markdown(
            "Paragraph line one\n"
            "line two\n"
            "\n"
            "> [!note]\n"
            "> keep this\n"
            "\n"
            "```python\n"
            "print('line one')\n"
            "print('line two')\n"
            "```\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "Paragraph line one line two\n"
            "\n"
            "> [!note]\n"
            "> keep this\n"
            "\n"
            "```python\n"
            "print('line one')\n"
            "print('line two')\n"
            "```\n",
        )

    def test_formats_inline_footnotes_outside_yaml(self) -> None:
        path = self.write_temp_markdown(
            "---\n"
            "title: diversified revenue stream.3\n"
            "---\n"
            "\n"
            'A diversified revenue stream.3 and "livable luxury".46 help.\n'
            "\n"
            "Strong review aggregations.37) also matter.\n"
            "\n"
            "Version 3.14 should stay as is.\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "---\n"
            "title: diversified revenue stream.3\n"
            "---\n"
            "\n"
            'A diversified revenue stream.[^3] and "livable luxury".[^46] help.\n'
            "\n"
            "Strong review aggregations.[^37]) also matter.\n"
            "\n"
            "Version 3.14 should stay as is.\n",
        )

    def test_removes_unnecessary_escapes_outside_yaml(self) -> None:
        path = self.write_temp_markdown(
            "---\n"
            "title: occurred circa 2021\\.\n"
            "---\n"
            "\n"
            "\\[an Oregon/Idaho based traditional site-builder\\].\n"
            "\n"
            "occurred circa 2021\\.\n"
            "\n"
            "OHI \\- Formerly ARVC,\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "---\n"
            "title: occurred circa 2021\\.\n"
            "---\n"
            "\n"
            "[an Oregon/Idaho based traditional site-builder].\n"
            "\n"
            "occurred circa 2021.\n"
            "\n"
            "OHI - Formerly ARVC,\n",
        )

    def test_formats_reference_section_entries_as_footnotes(self) -> None:
        path = self.write_temp_markdown(
            "## References\n"
            "1. Site Plan\n"
            "7. Building Big Dreams\n"
            "\n"
            "## Next Section\n"
            "1. This should remain a numbered list\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "## References\n"
            "[^1]: Site Plan\n"
            "[^7]: Building Big Dreams\n"
            "\n"
            "## Next Section\n"
            "1. This should remain a numbered list\n",
        )

    def test_formats_plain_references_label_entries_as_footnotes(self) -> None:
        path = self.write_temp_markdown(
            "References\n"
            "1. Site Plan\n"
            "2. Building Big Dreams\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "References\n"
            "[^1]: Site Plan\n"
            "[^2]: Building Big Dreams\n",
        )

    def test_formats_trailing_ordered_list_as_footnotes_without_named_heading(self) -> None:
        path = self.write_temp_markdown(
            "Some body text with retirement dwellings.2\n"
            "\n"
            "Closing section\n"
            "1. Site Plan\n"
            "7. Building Big Dreams\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "Some body text with retirement dwellings.[^2]\n"
            "\n"
            "Closing section\n"
            "[^1]: Site Plan\n"
            "[^7]: Building Big Dreams\n",
        )

    def test_cli_accepts_multiple_files(self) -> None:
        first = self.write_temp_markdown("Line one\nline two\n")
        second = self.write_temp_markdown("- bullet one\ncontinued\n")

        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "clean_markdown.py"), str(first), str(second)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Cleaned:", result.stdout)
        self.assertEqual(first.read_text(encoding="utf-8"), "Line one line two\n")
        self.assertEqual(second.read_text(encoding="utf-8"), "- bullet one continued\n")


if __name__ == "__main__":
    unittest.main()
