# arXiv Submission — EDEM Paper

Submission package for:

> **Estimated Dynamic Equilibrium Model: Supply and Demand as a Sample Path of a Stochastic Process**
> — Mikhail Arbuzov and Sisong Bei, 2026.

Source files: [`edem/`](edem/). Final upload bundle: [`edem_arxiv.zip`](edem_arxiv.zip) (~5.7 MB, 28-page PDF when arXiv auto-builds it).

## What's in the zip

```
main.tex              # \documentclass entry point — arXiv auto-detects this
main.bbl              # pre-built bibliography (so arXiv doesn't re-run bibtex)
references.bib        # bib source, included for transparency
sections/             # 11 .tex files (abstract through appendices)
figures/fig1..fig9.pdf  # 9 figure PDFs referenced from §5 (incl. sensitivity heatmap)
```

`main.pdf` and intermediate build artefacts (`*.aux`, `*.log`, `*.out`,
`*.blg`) are excluded — arXiv builds its own PDF.

## Local build (sanity check before upload)

```bash
cd edem
bash build.sh   # xelatex + bibtex + xelatex × 2  → main.pdf
bash pack.sh    # rebuilds ../edem_arxiv.zip
```

The build script extends `PATH` with the locations of MiKTeX
(`%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64`) and Pandoc on this
machine.

## Submission metadata

Copy the values below directly into the arXiv submission form.

| Field | Value |
|---|---|
| Title | Estimated Dynamic Equilibrium Model: Supply and Demand as a Sample Path of a Stochastic Process |
| Authors | Mikhail Arbuzov; Sisong Bei |
| Affiliation | — |
| Email (contact) | (fill in at submission time) |
| Primary category | `econ.GN` (General Economics) |
| Cross-list categories | `q-fin.GN` (General Finance); `cs.MA` (Multi-Agent Systems); `nlin.AO` (Adaptation and Self-Organizing Systems) |
| License | CC-BY-4.0 |
| Comments | 28 pages, 9 figures. Source code: see in-paper URL. |

### Primary-category decision

`econ.GN` was chosen over `q-fin.GN` because the paper's central
contribution is theoretical (extends Walrasian and Miller-divergence
frameworks) rather than financial-instrument-specific. The cross-list
`q-fin.GN` is included so finance-track readers can find it, and
`cs.MA` / `nlin.AO` cover the agent-based and complex-systems
audiences.

### Endorsement

This is likely a first-time submission to `econ.GN`. arXiv may require
endorsement from a published author in that category. If endorsement is
prompted at submission time, contact a co-author or department colleague
who has published on arXiv in econ.GN (or in any economics arXiv
category — they may be able to endorse cross-category).

## Plain-text abstract for the arXiv form

arXiv renders the abstract verbatim — strip LaTeX before pasting. Use
this version:

> We present the Estimated Dynamic Equilibrium Model (EDEM), an
> agent-based framework in which supply and demand are realisations
> of a coupled stochastic process driven by heterogeneous,
> error-prone agent valuations. The framework's central technical
> contribution is a generative mechanism for persistent
> disequilibrium: when market-clearing prices are repeatedly selected
> from the upper tail of noisy bid distributions and fed back into
> future valuations, expected prices drift upward even with strictly
> zero-mean estimation errors. We derive the bias in closed form for
> a clean special case (sigma*(n-1)/(n+1) for n iid uniform bids) and
> show via simulation that compounding the bias across epochs
> produces exponential price growth without any behavioural
> assumption about investor optimism. EDEM extends Miller's (1977)
> divergence-of-opinion theory to a fully dynamic setting and
> recovers Walrasian equilibrium and Miller's static premium as
> limiting cases. Eight controlled experiments in the Python ABM
> framework Mesa, on a 32x32 real-estate neighbourhood, demonstrate
> six qualitatively distinct regimes—band-stable, business-cycle,
> persistent overshoot, persistent undershoot, runaway bubble, and
> constant transition—all reachable from the same agent ruleset.
> Implications for the empirical divergence-of-opinion literature
> (which has produced contradictory findings) and for
> machine-learning valuation algorithms (which inherit and amplify
> the order-statistic bias) are discussed.

## Pre-submission checklist

- [x] Single LaTeX entry point with `\documentclass`
- [x] All figures referenced are bundled (8/8 present as PDF)
- [x] Filenames are arXiv-compliant (`a-z 0-9 _ + - .` only; lowercase)
- [x] Relative paths in `\includegraphics` (via `\graphicspath{{figures/}}`)
- [x] No build artefacts (`main.pdf`, `*.aux`, `*.log`) in the zip
- [x] `main.bbl` included so arXiv skips bibtex
- [x] xelatex compiles cleanly (0 unresolved labels, 0 unresolved citations)
- [x] Local PDF previews at 27 pages, 6.3 MB
- [x] Plain-text abstract ready for the form
- [ ] **Author has logged into arxiv.org and confirmed account is in good standing**
- [ ] **Code repository URL committed before submission**
- [ ] **Reviewed PDF page-by-page (figures, equations, tables, references)**

## Submit

1. Log in at <https://arxiv.org/user>.
2. Click "Start New Submission".
3. Upload `edem_arxiv.zip`.
4. Wait for arXiv's automatic compilation; verify the preview PDF
   matches the local 28-page build.
5. Fill metadata from the table above.
6. Paste the plain-text abstract.
7. Pick categories: primary `econ.GN`; cross-lists
   `q-fin.GN, cs.MA, nlin.AO`.
8. Pick license CC-BY-4.0.
9. Accept agreements; submit.

Submissions received by 14:00 US Eastern announce at 20:00 same day.
Local time check: <http://arxiv.org/localtime>.

## After announcement

Record the assigned arXiv ID below for citation in any future
revisions or companion papers.

- arXiv:XXXX.XXXXX (assigned YYYY-MM-DD)

For corrections after announcement, use the **Replace** flow on the
existing arXiv ID — never create a new submission.
