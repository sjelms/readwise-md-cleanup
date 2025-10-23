# Readwise Markdown Cleanup

---

## 📌 Intent
Fixes broken line breaks and formatting issues that occur when highlights from Apple Books are extracted by Readwise and then synced into markdown-based apps like Obsidian or Notion. This script focuses specifically on highlight formatting artifacts caused during this extraction and sync process.

- Preserves Obsidian-specific formatting like callouts (`> [!note]`), tags, and blockquotes.

---

## ⚙️ Actions
List the primary functions or operations this project performs. What does it actually do?
- Detects and merges broken multi-line highlights into a single paragraph
- Preserves associated `Tags:` and `Note:` sub-bullets
- Avoids modifying YAML front matter or any other non-highlight content
- Operates only on expected highlight structures typical of `Apple Books > Readwise > Obsidian` export chain

- Skips lines starting with Markdown syntax characters (`#`, `!`, `[`, `*`, `>`) to avoid corrupting headings, images, and callouts.

---

## 📥 Input
Describe the necessary inputs for this project. What data, files, or resources does it require to function?
- Input file type and format: Markdown (.md)
- Required format: Bullet list structure with indented tags or notes
- This should be an export from Apple Books or copy-pasted highlights in that style

---

## 📤 Output
Detail what the project produces.
- The same markdown file, updated in-place
- No filename or location change
- Git is recommended to track and undo changes if needed

---

### 🖱️ Quick Action (macOS Finder Right-Click)

To enable the right-click Finder action:

1. Download or clone this repo.
2. Open the `Quick Actions/Clean .md Highlights.workflow` file.
3. Double-click it to install into Automator.
4. Once added, right-click any `.md` file in Finder and choose `Quick Actions → Clean .md Highlights`.

### Automator command using the project .venv
If you previously used Homebrew Python like `/opt/homebrew/bin/python3` and saw “no such file or directory”, update the Automator action to call the project’s virtual environment Python directly.

In Automator’s “Run Shell Script” action, set:
- Shell: `/bin/zsh`
- Pass input: `as arguments`

Script:

```
/Users/stephenelms/Dev/readwise-md-cleanup/.venv/bin/python \
  "/Users/stephenelms/Dev/readwise-md-cleanup/clean_highlights.py" "$@"
```

Notes:
- Make sure you’ve created the venv first: `bash /Users/stephenelms/Dev/readwise-md-cleanup/setup_venv.sh`.
- If your repo is in a different folder, update the two absolute paths accordingly.
- This avoids relying on system or Homebrew Python paths that may differ across machines.

---

## 🧱 Framework
Outline the technology stack and setup instructions.
- **Primary Language/Framework:** Python 3
- **Dependencies:**
  - No external libraries required (standard library only)

### 🐍 Virtual Environment (.venv)
This project provides a helper script to create a local virtual environment and install dependencies.

Setup steps:
```bash
# from the project root
bash setup_venv.sh
# activate (optional)
source .venv/bin/activate
```

Install dependencies (already handled by setup_venv.sh):
```bash
.venv/bin/pip install -r requirements.txt
```

Run the script:
```bash
.venv/bin/python clean_highlights.py path/to/your/file.md
```

---

## 🛠️ Troubleshooting

List common problems and their solutions.

### 🟥 Problem: File doesn't update after running script

✅ Make sure you're passing the correct `.md` file path to the script.

### 🟥 Problem: Script removes intentional line breaks

✅ This cleaner is only intended for Apple Books highlights. Use cautiously on manually formatted notes.

### 🟥 Problem: I want to preview changes before overwriting

✅ Make a copy of your markdown file or use git to track file changes.

### 🟥 Problem: Obsidian callouts or metadata formatting breaks after cleanup

✅ The script now skips any line starting with `>` and other special characters to preserve Obsidian callouts and metadata. If you're seeing issues, make sure you're running the latest version.

For enhancements or bug reports, please open an issue in the GitHub repository. [https://github.com/sjelms/readwise-md-cleanup](https://github.com/sjelms/readwise-md-cleanup)