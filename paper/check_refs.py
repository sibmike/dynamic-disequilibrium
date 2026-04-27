"""Static check: every \\cref{...} target has a matching \\label{...}."""

from __future__ import annotations

import glob
import re

LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
CREF_RE = re.compile(r"\\(?:cref|ref|Cref)\{([^}]+)\}")

labels: set[str] = set()
crefs: set[str] = set()
for f in sorted(glob.glob("sections/*.tex")):
    text = open(f, encoding="utf-8").read()
    labels.update(LABEL_RE.findall(text))
    for grp in CREF_RE.findall(text):
        crefs.update(s.strip() for s in grp.split(","))

missing = sorted(crefs - labels)
unused = sorted(labels - crefs)
print(f"Labels: {len(labels)}")
print(f"Crefs:  {len(crefs)}")
print(f"\nMissing labels (referenced but never defined): {len(missing)}")
for m in missing:
    print(f"  - {m}")
print(f"\nUnused labels (defined but never referenced): {len(unused)}")
for u in unused:
    print(f"  - {u}")
