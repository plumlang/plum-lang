#!/usr/bin/env bash
set -euo pipefail

# Run from the root of a fresh clone of plumlang/plum-lang.
# These paths are tracked in the current main branch.
git rm -f -- .DS_Store plum/.DS_Store
git rm -r -f -- plum/lexer/__pycache__
git rm -f -- package-lock.json

# Remove any other local Python/macOS cache artifacts.
find . -type d -name __pycache__ -prune -exec rm -rf {} +
find . -type f \( -name '*.pyc' -o -name '*.pyo' -o -name '.DS_Store' \) -delete
