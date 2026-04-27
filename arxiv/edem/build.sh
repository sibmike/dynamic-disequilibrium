#!/usr/bin/env bash
# Build the EDEM paper for arXiv submission.
#
# This is the LaTeX-only variant of the arxiv-paper-prep skill build:
# the paper is already in .tex form, so the pandoc Markdown->LaTeX step
# is skipped. The pipeline is:
#
#   xelatex (1) -> bibtex -> xelatex (2) -> xelatex (3)
#
# Three xelatex passes are needed because cleveref's section-name
# resolution depends on .aux written by the second pass.
#
# Produces: main.pdf
# Pack for arXiv after a clean build:
#   bash pack.sh                 # creates ../edem_arxiv.zip

set -euo pipefail
cd "$(dirname "$0")"

# MiKTeX and friends live under %LOCALAPPDATA% on this box; pre-extend PATH.
export PATH="$PATH:/c/Users/${USER:-${USERNAME:-mikea}}/AppData/Local/Programs/MiKTeX/miktex/bin/x64"
export PATH="$PATH:/c/Users/${USER:-${USERNAME:-mikea}}/AppData/Local/Pandoc"

command -v xelatex >/dev/null || { echo "ERROR: xelatex not found." >&2; exit 1; }
command -v bibtex  >/dev/null || { echo "ERROR: bibtex not found."  >&2; exit 1; }

echo "[1/4] xelatex pass 1"
xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null

echo "[2/4] bibtex"
bibtex main >/dev/null || true   # bibtex returns nonzero on warnings; keep going

echo "[3/4] xelatex pass 2 (resolve citations)"
xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null

echo "[4/4] xelatex pass 3 (resolve cross-refs)"
xelatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null

echo "Built: $(pwd)/main.pdf ($(stat -c%s main.pdf 2>/dev/null || stat -f%z main.pdf 2>/dev/null) bytes)"
