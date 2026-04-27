#!/usr/bin/env bash
# Build the arXiv submission zip.
#
# Includes the LaTeX sources, the pre-built bibliography (.bbl, so arXiv
# doesn't need to re-run bibtex), the figure PDFs, and the .bib for
# transparency. Excludes intermediate build artifacts and the rendered
# main.pdf (arXiv builds its own).

set -euo pipefail
cd "$(dirname "$0")"

# Requires that build.sh has already produced main.bbl
if [ ! -f main.bbl ]; then
    echo "ERROR: main.bbl missing. Run ./build.sh first." >&2
    exit 1
fi

OUT="../edem_arxiv.zip"
rm -f "$OUT"

/c/Users/mikea/anaconda3/python.exe -c "
import zipfile, os
files = [
    'main.tex',
    'main.bbl',
    'references.bib',
]
for f in sorted(os.listdir('sections')):
    if f.endswith('.tex'):
        files.append(f'sections/{f}')
for f in sorted(os.listdir('figures')):
    if f.endswith('.pdf'):
        files.append(f'figures/{f}')

with zipfile.ZipFile(r'$OUT', 'w', zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f)
        print(f'  + {f}')

import os
print(f'\nWrote {os.path.abspath(r\"$OUT\")} ({os.path.getsize(r\"$OUT\")} bytes)')
"
