# Current Task

Last updated: 2026-10-19

## Current Objective

Keep the Assignment I–II repository documentation concise and accurate after removing obsolete Markdown files.

## Current Status

Completed

## Completed

- Assignment I notebooks, saved aggregate outputs, EDA figures, report PDF, and presentation remain in the repository. Its video was reported by the student as uploaded separately.
- Assignment II code, six model/split results, aggregate outputs, six figures, a 12-slide deck, and a timed presentation script were published on `main`. The local Word/PDF report is 31 pages and remains excluded from Git.
- The Assignment II AI form was updated at the student's direction to the Assignment II title, 16 October 2026, Type 2 / Partial Use, and the student's 15% estimate. The form remains for the student's review and signature.
- The Markdown audit removed superseded NotebookLM handoffs, the completed planning draft, duplicate Assignment I presenter guides, and an ignored stale model summary. README now retains the official Assignment II deliverable requirements and points to the remaining documentation.

## Remaining Work

- Student reviews the Assignment II report interpretation and AI declaration, signs the form, verifies accessible dataset/code links, and checks the final submission package.
- Student reviews the slide/script, rehearses, records, and verifies a video no longer than 10 minutes.

## Technical Decisions

- Keep `AGENTS.md`, `README.md`, `notebooks/README.md`, `docs/runtime-prerequisites.md`, and this file for cross-device setup and continuity.
- Keep `docs/assignment2-technical-results.md` because it is generated from measured outputs and used by the slide builder; keep `assignment2-video-presentation-script.md` for the pending recording.
- Treat the official course guide as the source of assignment requirements. The README gives a short public summary; old NotebookLM exchanges are recoverable from Git history.
- Spark work is a local `local[4]` prototype. Assignment II compares Spark RF, scikit-learn RF, and Logistic Regression on hash and chronological splits; the graph represents seller-state → customer-state relations, not physical transit.

## Files Changed

- Removed five tracked Markdown drafts/guides and one ignored stale Markdown summary.
- Updated `.gitignore`, `README.md`, and `docs/current-task.md`.

## Known Issues / Risks

- The student's final academic interpretation, AI declaration signature, and Assignment II video are not verified complete.
- Raw CSV, Parquet, runtime, model predictions, and the Assignment II Word/PDF report remain local and ignored; another device must obtain inputs and regenerate local outputs.
- A local `stash@{0}` from the prior freeze preserves unrelated pre-existing changes. Do not drop or apply it as part of documentation cleanup.

## Validation

### Build

NOT RUN — Markdown-only cleanup; no application build needed.

### Tests

NOT RUN — no analytical code or generated results changed.

### Lint / Static Analysis

PASS — references to removed Markdown files were checked, and `git diff --check` found no whitespace errors.

## Environment Notes

- Windows project root: `D:\Private Project\bda\BDA_Olist_Project`; Python 3.11 and PySpark 4.0.4 run locally with Java 17 prepared by `setup_runtime.py`.
- Origin: `https://github.com/yanlis-lase-SSG7/2611-bigDataAnalitycs.git`; branch `main`.

## Recommended Next Step

Complete the student-owned report sign-off and video, then verify the submission package and links.

## Useful Commands

```powershell
git status --short
git diff --check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
