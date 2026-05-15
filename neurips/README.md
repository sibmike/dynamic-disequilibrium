# NeurIPS 2026 Submission Packages

This directory holds NeurIPS 2026 main-track submission packages for papers from this repository. Each paper lives in its own `paper_<slug>/` subfolder; the official template is shared across all papers in `_template_reference/`.

## Submission folders

| Folder | Title | Anonymisation | Status |
|---|---|---|---|
| [`paper_edem/`](paper_edem/) | Dynamic Disequilibrium: An Agent-Based Mechanism for Bubbles without Biased Agents | double-blind | prepared (post-deadline; see note) |

Each `paper_<slug>/` subfolder is a self-contained NeurIPS submission package, with its own `README.md` covering submission metadata, anonymisation notes, page-budget table, and rebuild instructions, and a `submission/` directory holding the upload artifacts.

## Shared deadlines (NeurIPS 2026 main track)

| Milestone | Date (AOE) |
|---|---|
| Abstract submission | May 4, 2026 |
| Full paper submission | May 6, 2026 |
| Author notification | September 24, 2026 |

The 2026 deadlines have already passed as of this writing. The `paper_edem/` package is prepared for circulation as a NeurIPS-formatted version and for the next applicable submission window.

## Shared template

`_template_reference/` holds the unmodified official NeurIPS 2026 formatting bundle. All paper subfolders copy `neurips_2026.sty` into their own `submission/` directory so each build is self-contained, but treat `_template_reference/` as the source of truth for any future paper added here.

| Asset | Source | Date verified |
|---|---|---|
| `_template_reference/neurips_2026.sty` | `https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip` (via `telegrapher_repo/neurips/`) | 2026-04-29 |
| `_template_reference/neurips_2026.tex` | (same ZIP) | 2026-04-29 |
| `_template_reference/checklist.tex` | (same ZIP) | 2026-04-29 |
| Template last updated | `2026-03-17` (per file mtime in the official ZIP) | — |
| Call for papers | `https://neurips.cc/Conferences/2026/CallForPapers` | 2026-05-15 |

## Adding a new paper

1. `mkdir paper_<slug>/submission`
2. Copy `_template_reference/neurips_2026.sty` and `_template_reference/checklist.tex` into `paper_<slug>/submission/`.
3. Write `main.tex` against the proven preamble (see `paper_edem/submission/main.tex` for a working example).
4. Adapt `paper_edem/submission/build.sh` (project-agnostic; no edits typically needed).
5. Fill out `paper_<slug>/submission/checklist.tex` (replace each `\answerTODO{}` and `\justificationTODO{}`).
6. Write `paper_<slug>/README.md` modelled on the existing per-paper README.
7. Add the new paper to the table at the top of this file.
