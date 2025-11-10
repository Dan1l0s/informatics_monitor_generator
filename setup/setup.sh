#!/bin/bash

VENV_DIR="../venv"

python3 -m venv "$VENV_DIR"

source "$VENV_DIR/bin/activate"

pip install --upgrade pip

if [ -f ../requirements.txt ]; then
    pip install -r ../requirements.txt
fi

echo "Created venv in $VENV_DIR and installed dependencies!"
echo "Further venv activation: source $VENV_DIR/bin/activate"
