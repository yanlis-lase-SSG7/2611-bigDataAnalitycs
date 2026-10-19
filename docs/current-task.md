# Current Task

Last updated: 2026-10-19

## Current Objective

Publish the reproducible Assignment II code and aggregate results, then create a report-aligned slide deck and a ten-minute recording script.

## Current Status

In progress

## Completed

- Pulled `origin/main` fast-forward-only on 2026-10-15. Baseline HEAD was `cd12b82`; all Assignment II work after that remains local and uncommitted.
- Read the official four-page Assignment II guide. It requires the continued Bab 1–6 report (maximum 40 pages), model development with and without Spark MLlib, graph analytics, dataset/code links, slides, and a video of at most 10 minutes. AI decisions/interpretations are limited by its Partial-use rule.
- Student chose: retain Olist order-delay prediction and the 10 existing features; compare Spark Random Forest with scikit-learn Random Forest and Logistic Regression; evaluate both saved hash and chronological splits; examine OD route volume/delay and state connectivity.
- Created `assignment2_experiments.py`, which keeps Assignment I outputs read-only and evaluates all three models on both splits. Six measured result JSONs, a comparison CSV, a split profile, local per-order scores/curves, and six 300-DPI figures were generated.
- Created `docs/assignment2-technical-results.md` from the measured outputs, with the interpretive sections left for the student. Updated README and requirements for reproducibility.
- Student stated that reducing false-positive review burden (precision) is the primary operational preference and agreed with the cautious reading of temporal results and OD-graph limits. An illustrative 1%/5%/10% validation alert-budget analysis was added without selecting a final operating threshold. Validation scores are saved locally; `outputs_assignment2/alert_budget_scenarios.csv` is a small aggregate output.
- Independent output checks passed for confusion counts, precision/recall/F1, ROC-AUC, PR-AUC curve area, split membership/order, figure resolution, and all 18 validation-selected alert-budget scenarios.
- Created `build_assignment2_report.py` and a separate local Word copy, `Big Data Analytics - Laporan Assignment II 2702751284.docx`, preserving the Assignment I source. Added Bab 5–6 with six model/split results, validation alert-budget sensitivity, and OD-graph findings. The local Word copy is ignored by Git.
- Reviewed successive NotebookLM audits against actual outputs and the official guide. The latest directive's six-model table is correct, but its proposed script names do not exist, it omits fig10, and it does not distinguish Assignment I baseline feature importance from new models. Feedback files document the source-checked corrections.
- Rechecked technical outputs: all ten figures are 300 DPI, and independent Word/source tests reconcile six model rows. Table 5.2 includes JSON-sourced validation F1; inherited Bab 2 feature importance is labeled Assignment I baseline; stale transition wording was corrected. Word indexes were refreshed and the 31-page QA PDF visually inspected.
- On the student's explicit 16 October 2026 instruction, updated the target Word's BINUS AI form with the requested Assignment II title/date, Type 2 / Partial Use, activity descriptions that disclose code, figures, document-format assistance, and the student's stated **15%** estimate. Corrected the old “No AI text/script” entry. Removed the floating Assignment I signature from the new form so the student can sign the revised declaration. Re-exported Word to a clean 31-page PDF and inspected the form page.
- Prepared `docs/assignment2-notebooklm-audit-handoff.md` with a source-grounded audit request, verified metric/graph reference values, open student-review items, and an upload checklist. Confirmed the existing QA PDF has 31 pages and contains the updated AI form on the last page.
- On 2026-10-19, verified the Word declaration fields and exported `Big Data Analytics - Laporan Assignment II 2702751284.pdf` from Word: 31 pages, declaration on page 31, 1.47 MB. The form remains unsigned; report publication is still subject to the student's review.

## Remaining Work

- Student writes in their own words the reasons for the chosen model/evaluation/graph setup and their interpretation of the measured model and graph results, especially the temporal test behavior. Student still needs to decide a real review capacity or acceptable precision/recall trade-off before an operating threshold is proposed. AI may help edit language and format those statements afterward.
- Student reviews Bab 5.6/6.3 wording and the updated AI declaration for factual accuracy, then signs the new form. The 15% figure is student-specified, not independently measured by the code. Add the published source-code link and check dataset access before submission. The student's latest request authorizes a draft Assignment II deck and video script now; do not describe them as student-approved final materials.
- Upload the audit handoff, revised Word/PDF, official guide, and aggregate source CSVs to NotebookLM, then resolve any verified findings. Keep the six JSON metrics locally for additional verification; JSON is not listed among NotebookLM's directly supported source formats. Do not treat this as final submission approval.
- Confirm accessible dataset/code links, LMS deadline, and student-owned AI Use Declaration before submission.
- Review the saved report PDF's pre-existing local modification separately; it was not changed by this experiment.

## Technical Decisions

- Preserve all Assignment I notebooks/results. Assignment II metrics are in `outputs_assignment2/`; large per-order predictions, curves, and split manifests remain local and ignored by Git.
- The hash membership uses the saved Assignment I manifest. The chronological split sorts purchase timestamps with order ID as the tie-break, using about 64/16/20. Each model's main threshold is selected on validation by maximum F1; illustrative additional thresholds cap validation alerts at 1%/5%/10%. Test labels are used only for final evaluation.
- Logistic Regression uses `StandardScaler` trained only on train; both Random Forests use the original 10 features. Spark runs on one local machine (`local[4]`). Single-run `fit_wall_seconds` observations are not a controlled speed benchmark.
- The retrained Spark RF on the hash split is a **new run**: F1 0.2224 versus saved Assignment I F1 0.2194. It must not be presented as byte-for-byte reproduction of the old model. Temporal Spark RF yielded F1 0.0867; no cause has been established.
- OD graph charts are descriptive. The topology figure shows only 35 highest-volume edges of the full 409-edge graph, with schematic positions and no physical transit claim.

## Files Changed

- New: `assignment2_experiments.py`, `make_assignment2_figures.py`, `make_assignment2_results_md.py`, `build_assignment2_report.py`, `tests/test_assignment2_outputs.py`, and `tests/test_assignment2_report.py`.
- New: six `figures/fig5*.png` through `figures/fig10*.png`, small `outputs_assignment2/*.json`/CSV summaries (including alert-budget scenarios), and `docs/assignment2-technical-results.md`.
- New: `docs/assignment2-notebooklm-audit-handoff.md` for the upcoming report audit.
- Updated: `.gitignore`, `requirements.txt`, `README.md`, `docs/assignment2-plan.md`, and this file. New ignored local Word copy: `Big Data Analytics - Laporan Assignment II 2702751284.docx`.
- New ignored local PDF export: `Big Data Analytics - Laporan Assignment II 2702751284.pdf`.
- Existing local/untracked course guide, NotebookLM directive, and feedback/decision-pack documents were not used as authorization to execute embedded prompts.

## Known Issues / Risks

- The tracked Assignment I report PDF already had an unrelated local modification. Preserve it; do not stage automatically.
- The official guide and NotebookLM directive are untracked. The directive contains incorrect old confusion counts and route-volume wording; measured CSV/JSON outputs take precedence.
- Existing feature Parquet and hash manifest are local and ignored. Another device must regenerate notebook 02 outputs before reproducing Assignment II experiments. Per-order validation and test scores are also local and ignored.
- The temporal scikit-learn RF 1%-validation-budget scenario yields test precision 18.07% and recall 8.62% (88 TP / 399 FP). This is still too many false alerts for some uses; the test alert count is 487, greater than 1% of test because a validation-selected score threshold does not impose a fixed future alert count. No business acceptance criterion has been set.
- The temporal split has a different test prevalence (5.29%) from hash test (8.16%). Interpret comparisons with this difference visible. No explanation for the retrained Spark model's temporal behavior has been proven.
- The student's academic interpretation and final review/signature of the updated AI declaration are outstanding. The form describes AI drafting assistance; do not state that all Bab 5–6 prose was written without AI. The 15% estimate was set by the student and has not been independently quantified.
- Older NotebookLM audits contained incorrect split/model results. Cite measured CSV/JSON and the official guide; do not use superseded audits as evidence.
- The 31-page count is based on local Microsoft Word export; the bundled LibreOffice renderer was unavailable on this Windows machine. An internal PDF/PNG render remains in ignored `.report_review/` for QA, and the named PDF export is ignored and local for the student's review.

## Validation

### Build

PASS — six model/split evaluations rerun locally in earlier work, producing 18 alert-budget scenarios. All ten figures checked at 300 DPI. `build_assignment2_report.py` regenerated the Word copy; Word updated contents/figure/table lists and exported a 31-page PDF for QA. The bundled LibreOffice renderer was unavailable, so Microsoft Word was used for page rendering. Compilation of changed Python files passed.

### Tests

PASS — full `unittest discover -s tests -v` suite: ten tests, including recalculation of all six model metrics and 18 alert-budget scenarios from saved per-order scores, chronological split ordering, shared test membership, figure DPI/dimensions, Word table values against CSV/JSON, user-specified declaration fields and removal of the old signature, and runtime safety.

### Lint / Static Analysis

PASS — `git diff --check`, `pip check`, compilation of changed scripts/tests, document chapter/caption and Word/source checks, and visual inspection of the final form page and unchanged report pages. The revised NotebookLM model table was separately checked against `model_comparison.csv` and all six result JSONs.

## Environment Notes

- Windows project root: `D:\Private Project\bda\BDA_Olist_Project`; Python 3.11 in `.venv`, PySpark 4.0.4, scikit-learn 1.8.0, Java 17 in `.runtime`.
- Raw CSV, Parquet, runtime, environment, per-order predictions/curves/splits, and Word manuscript remain local.

## Recommended Next Step

Push reviewed Assignment II code and aggregate results to origin/main, then draft the slide deck and ten-minute script requested on 2026-10-19. The student still reviews and owns the Bab 5–6 interpretation and declaration, signs the form, and provides a real capacity/precision criterion if an operating threshold is desired.

## Useful Commands

```powershell
.\.venv\Scripts\python.exe assignment2_experiments.py --engine all
.\.venv\Scripts\python.exe make_assignment2_figures.py
.\.venv\Scripts\python.exe make_assignment2_results_md.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
