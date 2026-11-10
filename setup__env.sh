#!/bin/bash

# Exit immediately if any command fails, treating unset variables as errors
set -euo pipefail

echo "=== 0. Checking for Git Repository Updates ==="
if [ -d ".git" ]; then
    echo "Fetching latest updates from GitHub..."
    git pull || { echo "Error: Failed to pull updates from Git repository."; exit 1; }
else
    echo "Warning: Not a Git repository directory. Skipping git pull."
fi

echo "=== 1. Updating System Packages ==="
if ! sudo apt update && sudo apt upgrade -y; then
    echo "Error: Failed to update system packages." >&2
    exit 1
fi

echo "=== 2. Installing System-Level Dependencies ==="
if ! sudo apt install -y python3-tk python3-venv portaudio19-dev espeak alsa-utils git; then
    echo "Error: Failed to install system-level dependencies." >&2
    exit 1
fi

echo "=== 3. Setting Up Python Virtual Environment ==="
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    if ! python3 -m venv venv; then
        echo "Error: Failed to create Python virtual environment." >&2
        exit 1
    fi
    echo "Virtual environment created successfully."
fi

echo "=== 4. Activating Virtual Environment and Installing Python Libraries ==="
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment activation script not found." >&2
    exit 1
fi

if ! pip install --upgrade pip; then
    echo "Error: Failed to upgrade pip." >&2
    exit 1
fi

if ! pip install vosk requests sounddevice pyttsx3; then
    echo "Error: Failed to install required Python libraries." >&2
    exit 1
fi

echo "=== Setup Complete Successfully! ==="
echo "To activate your environment later, run: source venv/bin/activate"