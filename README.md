# Title
Readwise Markdown Cleanup

---

## 📌 Intent
Fixes broken line breaks and formatting issues that occur when highlights from Apple Books are extracted by Readwise and then synced into markdown-based apps like Obsidian or Notion. This script focuses specifically on highlight formatting artifacts caused during this extraction and sync process.

---

## ⚙️ Actions
List the primary functions or operations this project performs. What does it actually do?
- Detects and merges broken multi-line highlights into a single paragraph
- Preserves associated `Tags:` and `Note:` sub-bullets
- Avoids modifying YAML front matter or any other non-highlight content
- Operates only on expected highlight structures typical of `Apple Books > Readwise > Obsidian` export chain

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

## 🧱 Framework
Outline the technology stack and setup instructions.
- **Primary Language/Framework:** Python 3
- **Dependencies:**
  - No external libraries required (standard library only)

Provide the command to install dependencies:
```bash
# No dependencies required
```

Provide the command to run the script:
```bash
python clean_applebooks_md.py path/to/your/file.md
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

For enhancements or bug reports, please open an issue in the GitHub repository. [https://github.com/sjelms/*](https://github.com/sjelms/*)