#!/usr/bin/env bash

# Poetry setup
poetry env use python3.12
poetry install --with test --sync
poetry lock
poetry update --sync

# Pre-commit setup
pre-commit install

# Create .env file
if [[ ! -f .env ]]; then
  cat > .env <<EOF
PATH="./src:./tests:\$PATH"
PYTHONPATH="./src:./tests:\$PYTHONPATH"
EOF
else
  echo -e "\033[0;33m.env file already exists. Skipping...\033[0m"
fi

# Create build directory if it doesn't exist
mkdir -p build
