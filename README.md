# Markdown Cleanup

Small Python utility for normalizing imported markdown in place. It targets soft-wrapped paragraphs and list items from exported notes, highlights, and copied markdown while preserving common markdown structure.

## What It Does

- Merges soft-wrapped paragraphs into a single line
- Merges wrapped list items without flattening nested lists
- Preserves YAML front matter, headings, blockquotes, callouts, fenced code blocks, and tables
- Keeps Readwise-style nested `Tags:` and `Note:` bullets intact
- Processes one file, many files, or an entire directory tree of `.md` files

## What It Expects

- Markdown files that should be normalized in place
- Best fit: exported highlights, clipped notes, and markdown that has unwanted line breaks
- Less suitable: prose where manual line breaks are intentional

## CLI Usage

Set up the local virtual environment:

```bash
bash setup_venv.sh
```

Run against one file:

```bash
.venv/bin/python clean_markdown.py /path/to/file.md
```

Run against multiple files or a directory:

```bash
.venv/bin/python clean_markdown.py /path/to/file-one.md /path/to/file-two.md /path/to/folder
```

`clean_highlights.py` remains as a compatibility wrapper for older automation setups.

## Private Local Config

To keep your local path out of the repo:

1. Copy `.env.local.example` to `.env.local`
2. Set `MARKDOWN_CLEANUP_ROOT` to your local checkout path

`.env.local` is gitignored and used by the Quick Action installer.

## macOS Quick Action

The workflow stored in the repo is now a template and contains no personal path. Install a local copy with your private path injected from `.env.local`:

```bash
bash install_quick_action.sh
```

By default this installs to `~/Library/Services`. Finder should then show `Quick Actions -> Clean Markdown`.

## Verification

Regression tests:

```bash
.venv/bin/python -m unittest discover -s tests
```

Representative coverage includes:

- wrapped paragraphs
- wrapped list items with nested lists
- Readwise-style `Tags:` and `Note:` bullets
- multiple file arguments

## Legacy Helper

`readwise-tag-suffix-amend.sh` is still present for Readwise-specific tag cleanup. It is separate from the general markdown normalizer.
