#!/bin/bash

# Exit immediately if any command fails
set -e

# 1. Navigate to the project directory (adjust path if needed)
cd "$(dirname "$0")"

echo "=== Checking for repository updates ==="
if [ -d ".git" ]; then
    # Pull latest changes from GitHub
    git pull || { echo "Warning: Git pull failed (offline or merge conflict). Continuing with local version..."; }
else
    echo "Notice: Not a git repository."
fi

echo "=== Activating Virtual Environment ==="
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found! Please run setup_env.sh first." >&2
    exit 1
fi

echo "=== Launching Mambo Assistant ==="
python3 main.py