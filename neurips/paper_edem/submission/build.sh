#!/usr/bin/env bash
# Build the NeurIPS 2026 submission PDF: pdflatex -> bibtex -> pdflatex x 2.
#
# Requires: pdflatex (TeX Live or MiKTeX), bibtex.
# Produces: main.pdf, main.bbl, main.aux, etc.

set -euo pipefail
cd "$(dirname "$0")"

# Common Windows install locations (harmless on macOS/Linux).
export PATH="$PATH:/c/Users/${USER:-${USERNAME:-}}/AppData/Local/Programs/MiKTeX/miktex/bin/x64:/c/Program Files/MiKTeX/miktex/bin/x64"

command -v pdflatex > /dev/null || { echo "ERROR: pdflatex not found. Install MiKTeX (Win), MacTeX (Mac), or TeX Live (Linux)." >&2; exit 1; }
command -v bibtex   > /dev/null || { echo "ERROR: bibtex not found." >&2; exit 1; }

echo "[1/4] pdflatex pass 1"
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null

echo "[2/4] bibtex"
bibtex main > /dev/null

echo "[3/4] pdflatex pass 2 (resolve citations)"
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null

echo "[4/4] pdflatex pass 3 (resolve cross-refs)"
pdflatex -interaction=nonstopmode -halt-on-error main.tex > /dev/null

echo "Build complete: main.pdf"
ls -la main.pdf
