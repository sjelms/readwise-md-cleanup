#!/usr/bin/env bash
set -euo pipefail

# Append "-rw" to specific Readwise source tags in markdown files, idempotently.
#
# Changes (exact-line matches only):
# - "tags: articles"   -> "tags: articles-rw"
# - "tags: books"      -> "tags: books-rw"
# - "tags: podcasts"   -> "tags: podcasts-rw"
# - "tags: tweets"     -> "tags: tweets-rw"
# - "> - Category: #articles"   -> "> - Category: #articles-rw"
# - "> - Category: #books"      -> "> - Category: #books-rw"
# - "> - Category: #podcasts"   -> "> - Category: #podcasts-rw"
# - "> - Category: #tweets"     -> "> - Category: #tweets-rw"
#
# YAML safety and cleanup:
# - Split merged lines like "tags: ...-rwdocument-tags:" into two lines
# - Split "document-tags: ---" into separate lines
# - Normalize "document-tags::" to "document-tags:"
# - Convert inline "document-tags: - ..." to proper YAML list:
#     document-tags:
#       - "[[...]]"
# - Remove blank separator line immediately after "document-tags:" if followed by a list item
# - Split merged metadata lines "> - Category: #...-rw> - Document Tags:" onto two lines
#
# Usage:
#   ./rw_tag_suffix_rw.sh [path]
#     - path: file or directory to process (default: current directory)
#     - safe to re-run; no double "-rw" and YAML stays clean

root_target="${1:-.}"

files_list=()
if [[ -f "$root_target" ]]; then
  files_list+=("$root_target")
elif [[ -d "$root_target" ]]; then
  while IFS= read -r -d '' f; do files_list+=("$f"); done < <(find "$root_target" -type f -name "*.md" -print0)
else
  echo "Error: '$root_target' is not a file or directory" >&2
  exit 1
fi

# Update files in-place.
for file in "${files_list[@]}"; do
  # Update tags: <type>
  perl -i -pe 's/^tags:\s*(articles|books|podcasts|tweets)\s*$/tags: $1-rw/i' "$file"

  # Update optional quoted Category lines: "> - Category: #<type>"
  perl -i -pe 's/^\s*(>\s*)?- Category:\s*#(articles|books|podcasts|tweets)\s*$/${1}- Category: #$2-rw/i' "$file"

  # Cleanup: ensure a line break exists between "tags: <type>-rw" and a following "document-tags:" if they merged.
  perl -i -pe 's/^\s*(tags:\s*(?:articles|books|podcasts|tweets)-rw)\s*(document-tags:)\s*$/$1\n$2/i; s/^\s*(tags:\s*(?:articles|books|podcasts|tweets)-rw)\s*(document-tags:)\b/$1\n$2/i' "$file"

  # Cleanup: ensure a line break exists between metadata lines if they merged.
  perl -i -pe 's/^\s*((?:>\s*)+-\s*Category:\s*#(?:articles|books|podcasts|tweets)-rw)\s*(>\s*-\s*Document\s+Tags:)/$1\n$2/i' "$file"

  # Cleanup: if "document-tags:" accidentally merged with YAML delimiter (---), split them.
  perl -i -pe 's/^(\s*document-tags::?\s*)---/$1\n---/i' "$file"

  # Cleanup: normalize any accidental double-colons after document-tags
  perl -i -pe 's/^\s*(document-tags)::\s*/$1: /i' "$file"

  # YAML: if document-tags is followed by an inline list item on the same line, split it onto the next line.
  perl -i -pe 's/^(\s*document-tags:)\s*-\s*(.+)\s*$/$1\n  - $2/i' "$file"

  # YAML: remove a blank line immediately after document-tags: if the next line is a list item.
  perl -0777 -i -pe 's/^(\s*document-tags:\n)[\ \t]*\n(\s*-\s)/$1$2/m' "$file"
done

echo "Done: appended -rw to matching tags and category lines under '$root_target'."
