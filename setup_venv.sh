#!/usr/bin/env bash
set -euo pipefail

# Create a local virtual environment in .venv and install requirements
# Usage: bash setup_venv.sh

# Choose python executable
PYTHON_BIN=${PYTHON_BIN:-python3}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: $PYTHON_BIN not found on PATH. Please install Python 3 and try again." >&2
  exit 1
fi

# Create venv if missing
if [ ! -d .venv ]; then
  echo "Creating virtual environment in .venv ..."
  "$PYTHON_BIN" -m venv .venv
else
  echo ".venv already exists. Skipping creation."
fi

# Upgrade pip tooling inside venv
./.venv/bin/python -m pip install --upgrade pip setuptools wheel

# Install project requirements
if [ -f requirements.txt ]; then
  echo "Installing requirements from requirements.txt ..."
  ./.venv/bin/pip install -r requirements.txt
else
  echo "No requirements.txt found — skipping dependency installation."
fi

# Show summary
./.venv/bin/python --version
./.venv/bin/pip --version

echo "Done. Activate with: source .venv/bin/activate"
