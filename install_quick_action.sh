#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/.env.local}"
DEST_DIR="${1:-$HOME/Library/Services}"
WORKFLOW_NAME="Clean .md Highlights.workflow"
WORKFLOW_TEMPLATE="$SCRIPT_DIR/$WORKFLOW_NAME"
DEST_WORKFLOW="$DEST_DIR/$WORKFLOW_NAME"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing $CONFIG_FILE" >&2
  echo "Copy .env.local.example to .env.local and set MARKDOWN_CLEANUP_ROOT first." >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$CONFIG_FILE"

PROJECT_ROOT="${MARKDOWN_CLEANUP_ROOT:-}"
if [[ -z "$PROJECT_ROOT" ]]; then
  echo "MARKDOWN_CLEANUP_ROOT is not set in $CONFIG_FILE" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_ROOT" ]]; then
  echo "Configured project root does not exist: $PROJECT_ROOT" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"
ditto "$WORKFLOW_TEMPLATE" "$DEST_WORKFLOW"

WORKFLOW_DOCUMENT="$DEST_WORKFLOW/Contents/document.wflow"
ESCAPED_ROOT="${PROJECT_ROOT//\//\\/}"
perl -0pi -e "s/__MARKDOWN_CLEANUP_ROOT__/$ESCAPED_ROOT/g" "$WORKFLOW_DOCUMENT"

echo "Installed Quick Action to $DEST_WORKFLOW"
