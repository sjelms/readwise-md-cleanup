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
            "    - **Tags:** [[blue]]\n"
            "    - **Note:** Keep this note\n",
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

    def test_preserves_decimals_and_formats_footnotes_inside_tables(self) -> None:
        path = self.write_temp_markdown(
            "| Metric | Value |\n"
            "| :---- | :---- |\n"
            "| Revenue estimate | $29.8 Million.1 |\n"
            "| Airtightness | 0.054 CFM/sq ft.2 |\n"
            "\n"
            "#### **Works cited**\n"
            "1. Revenue source\n"
            "2. Airtightness source\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "| Metric | Value |\n"
            "| :---- | :---- |\n"
            "| Revenue estimate | $29.8 Million.[^1] |\n"
            "| Airtightness | 0.054 CFM/sq ft.[^2] |\n"
            "\n"
            "#### **Works cited**\n"
            "[^1]: Revenue source\n"
            "[^2]: Airtightness source\n",
        )

    def test_formats_trailing_space_separated_citations_in_list_items(self) -> None:
        path = self.write_temp_markdown(
            "* *Building the Timberframe House: The Revival of a Forgotten Craft* (1980) 5\n"
            "* *The Timber-frame Home: Design, Construction, Finishing* (1988) 5\n"
            "* *The Timberframe Home* (Revised Edition, 1997\\) 5\n"
            "* *Timberframe: The Art and Craft of the Post-and-Beam Home* (1999) 5\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "* *Building the Timberframe House: The Revival of a Forgotten Craft* (1980) [^5]\n"
            "* *The Timber-frame Home: Design, Construction, Finishing* (1988) [^5]\n"
            "* *The Timberframe Home* (Revised Edition, 1997) [^5]\n"
            "* *Timberframe: The Art and Craft of the Post-and-Beam Home* (1999) [^5]\n",
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

    def test_normalizes_terminal_wrapped_star_bullets_to_spaced_dash_list(self) -> None:
        path = self.write_temp_markdown(
            "   * Felstead et al. (2011), which argues that the act of doing a job provides the primary opportunities for learning and development, framing it as\n"
            '     "Working to Learn, Learning to Work" [[-Felstead2011-az]].\n'
            "   * Derrick (2020), who explores \"practice-based learning\" and how innovation and learning emerge from the daily, indeterminate practices of the\n"
            "     workplace [[-Derrick2020-yv]].\n"
            "   * Billett (2001, 2008), whose work centers on \"learning through work\" and \"learning through workplace practice,\" highlighting the relational\n"
            "     interdependence between workplace affordances and the worker's active engagement in their tasks [[-Billett2001-xo]] [[-Billett2008-kx]].\n"
            "   * Broad & Lahiff (2019), who specifically discuss how vocational teachers develop and sustain expertise through practice and the \"process of\n"
            "     becoming\" within their professional community [[-Broad2019-rn]].\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            '- Felstead et al. (2011), which argues that the act of doing a job provides the primary opportunities for learning and development, framing it as "Working to Learn, Learning to Work" [[-Felstead2011-az]].\n'
            '- Derrick (2020), who explores "practice-based learning" and how innovation and learning emerge from the daily, indeterminate practices of the workplace [[-Derrick2020-yv]].\n'
            '- Billett (2001, 2008), whose work centers on "learning through work" and "learning through workplace practice," highlighting the relational interdependence between workplace affordances and the worker\'s active engagement in their tasks [[-Billett2001-xo]] [[-Billett2008-kx]].\n'
            '- Broad & Lahiff (2019), who specifically discuss how vocational teachers develop and sustain expertise through practice and the "process of becoming" within their professional community [[-Broad2019-rn]].\n',
        )

    def test_nests_terminal_wrapped_star_bullets_under_ordered_item(self) -> None:
        path = self.write_temp_markdown(
            "  1. Learning as a \"Discrete Product\" (The Acquisition Metaphor)\n"
            "  The most pervasive early assumption was that learning is a \"thing\".\n"
            "   * Assumption: Knowledge can be pre-specified.\n"
            "   * Note Example: Formal preparation is insufficient.\n"
            "\n"
            "  2. Behaviorism: Focus on the \"Observable\"\n"
            "  Behaviorism was dominant.\n"
            "   * Assumption: Learning is observable actions.\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            '1. Learning as a "Discrete Product" (The Acquisition Metaphor) The most pervasive early assumption was that learning is a "thing".\n'
            "\t- **Assumption:** Knowledge can be pre-specified.\n"
            "\t- **Note Example:** Formal preparation is insufficient.\n"
            '2. Behaviorism: Focus on the "Observable" Behaviorism was dominant.\n'
            "\t- **Assumption:** Learning is observable actions.\n",
        )

    def test_nests_dash_bullets_under_ordered_item(self) -> None:
        path = self.write_temp_markdown(
            "1. Heading\n"
            "Continuation line\n"
            "- Assumption: First point\n"
            "- Note Example: Second point\n"
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "1. Heading Continuation line\n"
            "\t- **Assumption:** First point\n"
            "\t- **Note Example:** Second point\n",
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

    def test_collapses_soft_wrap_gaps_and_inline_metadata_spacing(self) -> None:
        path = self.write_temp_markdown(
            '✦ Exploring Early Learning Models, noting "Behaviorism" and the "Economic Perspective"\n'
            "  \n"
            "  were dominant before situated learning and often ignored workplace context.\n"
            "  \n"
            '  [Thought: true]Before the rise of situated learning, models viewed learning as a "product".\n'
        )

        clean_markdown_file(path)

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            '✦ Exploring Early Learning Models, noting "Behaviorism" and the "Economic Perspective" were dominant before situated learning and often ignored workplace context. [Thought: true] Before the rise of situated learning, models viewed learning as a "product".\n',
        )


if __name__ == "__main__":
    unittest.main()
