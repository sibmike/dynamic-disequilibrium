#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

xelatex -interaction=nonstopmode main.tex
bibtex main || true
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex

echo "Built: $(pwd)/main.pdf"
