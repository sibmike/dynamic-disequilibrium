# NeurIPS 2026 Submission — Dynamic Disequilibrium / EDEM

This directory holds the NeurIPS 2026 main-track submission package
for the EDEM paper, anonymized and formatted with `neurips_2026.sty`
for double-blind review.

## Quick links

- **Paper PDF** (upload to OpenReview): [`submission/main.pdf`](submission/main.pdf)
- **LaTeX source**: [`submission/main.tex`](submission/main.tex)
- **Reproducible build**: `bash submission/build.sh`
- **Template reference (untouched, shared with sibling papers)**: [`../_template_reference/`](../_template_reference/)
- **arXiv preprint version** (separate, non-anonymized): [`../../arxiv/edem/`](../../arxiv/edem/)

## Submission metadata

| Field | Value |
|---|---|
| **Conference** | NeurIPS 2026 |
| **Track** | Main Track (double-blind) |
| **Style file** | `neurips_2026.sty` (official, dated 2026-03-17) |
| **Title** | Dynamic Disequilibrium: An Agent-Based Mechanism for Bubbles without Biased Agents |
| **Authors** | Anonymous (double-blind) |
| **Primary subject area** | Machine Learning theory / Applications (real-estate AVM bias) |
| **Page count** | Main body ≤ 9 pages + references + appendix + 7-page checklist |
| **Submission portal** | OpenReview (`NeurIPS.cc/2026/Conference`) |

## Pre-submission checklist

Build verification:

- [x] PDF builds via `bash submission/build.sh` (pdflatex → bibtex → pdflatex × 2)
- [x] Title page renders as `Anonymous Author(s) / Affiliation / Address / email`
- [x] Line numbers visible down the left margin (added by `neurips_2026.sty` for review)
- [x] Main body fits in ≤ 9 pages
- [x] References render with author/year style (`natbib` plainnat default)
- [x] Three figures inline (fig6 bubble, fig7 balancer sweep, fig9 sensitivity); six more figures in Appendix C
- [x] Tables render via `booktabs` (no vertical rules)
- [x] Mandatory paper checklist filled with paper-specific answers (16 questions: 12 Yes, 4 NA, 0 No)
- [x] No author-identifying information in the built PDF (no funding acknowledgements, no repository URLs, no institutional affiliations; verified via `pdftotext`)
- [x] Bibliography produced from `references.bib` via `bibtex` (18 entries)

Submission-time checks (do these in OpenReview):

- [ ] Upload `submission/main.pdf` as the paper
- [ ] Confirm anonymized author information on the OpenReview metadata form
- [ ] Select Main Track
- [ ] Set primary subject area; cross-list as appropriate
- [ ] Disclose conflicts of interest
- [ ] Acknowledge the funding/competing-interests disclosure (filled at camera-ready time, not submission)

## Anonymization notes

The paper has been anonymized for double-blind review:

1. **Author block**: `Anonymous Author(s) / Affiliation / Address / email` (no real names).
2. **Repository URL**: not referenced in the paper. The MIT-licensed Mesa codebase and the arXiv preprint URL are added to the camera-ready version.
3. **Self-citations**: the two 2018 SJSU working papers (`arbuzov2018de`, `arbuzov2018edem`) are cited in the third person; NeurIPS guidelines permit this for double-blind submissions.
4. **Acknowledgments**: omitted. The `\begin{ack} ... \end{ack}` environment provided by `neurips_2026.sty` would auto-hide them anyway; we have simply not written any in `main.tex`.

When preparing the camera-ready, switch the `\usepackage{neurips_2026}` line to `\usepackage[main, final]{neurips_2026}` to reveal authors.

For a non-anonymized preprint build (different from the NeurIPS submission), use the `[preprint]` option — that produces a version with "Preprint. Work in progress." in the footer. The arXiv preprint at `../../arxiv/edem/` already provides the equivalent non-anonymized build via xelatex.

## Tracks considered and not chosen

| Track | Why not |
|---|---|
| Position Paper | The paper has an empirical contribution and a method (the EDEM ABM); not a position piece, although §6 makes a position-style argument about ML valuation systems. |
| Evaluations & Datasets | EDEM's contribution is the method and mechanism, not a benchmark dataset. |
| Creative AI | Not a creative-AI paper. |
| Workshop | Main track is appropriate; workshop tracks are available as fallbacks. |

## Page budget

| Section | Approx. pages |
|---|---|
| §1 Introduction | 1.25 |
| §2 Background and Related Work | 0.75 |
| §3 The EDEM Framework | 1.75 |
| §4 The Order-Statistic Mechanism (+ Table 1) | 1.25 |
| §5 Experiments (3 figures + 1 table) | 2.5 |
| §6 Discussion: ML Valuation Implications | 1.0 |
| §7 Limitations and Conclusion | 0.5 |
| **Main body total** | **≤ 9** |
| References | 0.5 |
| Appendix A: ODD Protocol | 1.0 |
| Appendix B: Parameter Tables | 0.5 |
| Appendix C: All Experiment Figures (Figs 1-5, 8) | 2.0 |
| Appendix D: Extensions and Future Work | 1.0 |
| Mandatory paper checklist | 7.0 |
| **Document total** | ≤ 21 |

References, appendices, and the checklist do not count against the 9-page limit.

## Submission-specific adaptations

This NeurIPS package is built from the same underlying paper content as the arXiv preprint, using the conference-specific format. Key differences:

| Item | NeurIPS submission | arXiv preprint |
|---|---|---|
| Style file | `neurips_2026.sty` | custom xelatex preamble |
| Engine | `pdflatex` | `xelatex` |
| Page count | 9 main + appendix + checklist (~21 total) | 30 |
| Author block | Anonymous Author(s) | Mikhail Arbuzov and Sisong Bei |
| Repository URL | omitted (revealed in camera-ready) | https://github.com/sibmike/dynamic-disequilibrium |
| Bibliography | `natbib` author/year via `references.bib` (same bib file) | same |
| Mandatory checklist | included | omitted |
| Cross-refs | manual (`Eq.~\eqref{}`, `Fig.~\ref{}`) | `cleveref` |

## Rebuilding

```bash
# from this directory
bash submission/build.sh
```

The build runs `pdflatex` → `bibtex` → `pdflatex` × 2 to resolve citations and cross-references. Requires MiKTeX (Windows) or TeX Live (Linux/macOS) with `pdflatex` and `bibtex` on `PATH`. The build script pre-extends `PATH` for the standard Windows MiKTeX install location.

## Source of truth and provenance

| Asset | Source | Date verified |
|---|---|---|
| `../_template_reference/neurips_2026.sty` | NeurIPS 2026 ZIP (via `telegrapher_repo`) | 2026-04-29 |
| `../_template_reference/neurips_2026.tex` | (same ZIP) | 2026-04-29 |
| `../_template_reference/checklist.tex` | (same ZIP) | 2026-04-29 |
| Template last updated | `2026-03-17` (per file mtime in the official ZIP) | — |
| Call for papers | `https://neurips.cc/Conferences/2026/CallForPapers` | 2026-05-15 |

Note on deadline: NeurIPS 2026 abstract / full-paper deadlines (May 4 / May 6, 2026 AOE) have already passed as of the most recent verification date. This package is prepared as a NeurIPS-formatted version of the paper for circulation and for the next applicable submission window.
