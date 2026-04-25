#!/bin/bash
set -e

INDELPHI_DIR="/app/Indelphi_installation/inDelphi-model-master"

if [ ! -d "$INDELPHI_DIR" ]; then
    echo "inDelphi not found — cloning from GitHub..."
    mkdir -p /app/Indelphi_installation
    git clone https://github.com/maxwshen/inDelphi-model.git "$INDELPHI_DIR"
    echo "inDelphi cloned successfully."
else
    echo "inDelphi already present, skipping clone."
fi

export FLASK_ENV=production

exec python index.py
