# Codex workflow and project instructions

## Automatic session initialization

At every new Codex session or fresh repository context, before meaningful implementation work, automatically:
1. Read AGENTS.md and docs/current-task.md if it exists.
2. Inspect `git status` and `git log -5 --oneline`.
3. Read relevant project documentation and files relevant to the user's current request.
4. Compare documented state with actual source, outputs and Git state; correct stale documentation when needed.
5. Treat actual repository/source/Git history as more authoritative than stale documentation or previous chat history.

Do this as part of the first normal task. No resume/handoff command is required. Never depend on previous Codex chat history. Reading context does not authorize pulling, resetting, committing or publishing changes.

## Continuous documentation maintenance

Documentation maintenance is part of implementation. Whenever meaningful project state changes, automatically evaluate whether documentation became inaccurate or incomplete. Update only relevant files: docs/current-task.md, README, architecture, setup/environment, dependencies, API, database, or other project-specific documentation where applicable.

Do not touch files merely to create documentation activity. Persist important context in source, tests, configuration, README, permanent docs or docs/current-task.md. Necessary development context must not exist only in chat. Documentation updates alone do not authorize committing or pushing.

## docs/current-task.md policy

Maintain the actual CURRENT development state, not a session diary. Rewrite obsolete details instead of endlessly appending summaries. Git history is the historical record. Keep only information another session needs to continue correctly. Never store secrets or credentials.

Use this structure:

```markdown
# Current Task

Last updated: YYYY-MM-DD

## Current Objective

## Current Status

## Completed

## Remaining Work

## Technical Decisions

## Files Changed

## Known Issues / Risks

## Validation

### Build

### Tests

### Lint / Static Analysis

## Environment Notes

## Recommended Next Step

## Useful Commands
```

Current Status must be one of: Not started, In progress, Blocked, Ready for validation, Ready for review, or Completed. Record review/publication still pending; do not claim an unperformed commit, push, implementation or validation succeeded. Build, Tests and Lint / Static Analysis must use PASS, FAIL, NOT RUN or NOT AVAILABLE, with a short explanation of actual checks and limits. Update the date when the state changes.

## Automatic pre-commit synchronization

Whenever the user requests commit, create a commit, commit changes, save to Git, commit and push, push changes, or an equivalent action, automatically synchronize documentation first:
1. Inspect `git status`, `git diff` and `git diff --cached`.
2. Review all changes, including existing staged files. Preserve unrelated user work; do not silently include it.
3. Update docs/current-task.md to match actual state.
4. Update other documentation only when implementation changes made it inaccurate or incomplete.
5. Run appropriate validation where practical; record what ran, what did not, and why.
6. Re-inspect the resulting diff.
7. Confirm implementation and documentation agree, necessary context is persisted, no obvious secrets are included, and no inappropriate temporary/generated/large files are included.
8. Only then stage intended files, inspect the staged diff, run `git diff --cached --check` and commit.

The user must not separately request documentation synchronization. Do not create empty commits or invent updates if the repository is already accurate. Commit-only requests authorize a commit, not a push. Commit-and-push requests authorize both. For a push request, include a necessary documentation synchronization commit before publication, without silently committing unrelated implementation changes. Respect explicit instructions to leave work uncommitted or unpushed.

## Automatic pre-push synchronization

Before an authorized push:
1. Confirm documentation reflects committed state and important cross-device context is committed.
2. Inspect `git status` and `git log -3 --oneline`.
3. Confirm intended branch and remote: main and origin at https://github.com/yanlis-lase-SSG7/2611-bigDataAnalitycs.git.
4. Run appropriate validation if not already run for these changes; do not repeat checks without reason.
5. Push safely. If the remote advanced, inspect and integrate without discarding local work. Never force push unless explicitly requested.
6. After push, verify success, intended upstream tracking and equality of local HEAD with the intended remote branch. Verify no required cross-device context remains only locally; report unrelated local changes if any remain.

Every pushed commit should be a recoverable checkpoint for another laptop. If authentication or permissions block publication, document the actual blocker without credentials and report the user action needed. Never claim publication succeeded until verified.

## New task transition

When the request is clearly a different task, automatically review docs/current-task.md, preserve unresolved important information, move long-lived decisions into permanent documentation when appropriate, replace the active objective and remove irrelevant obsolete details. A clarification or status question about active work does not replace that work.

## Desired cross-device experience

OFFICE:
- User gives a normal task; Codex automatically reads repository context and works.
- Codex keeps relevant development state and documentation current.
- User says "commit and push"; Codex synchronizes docs, validates, commits and pushes.

HOME:
- User runs git pull / Get Latest and opens the project in VS Code.
- User immediately gives a normal development task.
- Codex automatically reads repository context and continues from actual source/Git state.

No special resume/handoff command is required. These instructions guide Codex sessions using the repository; they are not a background daemon or Git hook. Changes made outside Codex must be checked against actual state on the next session. An initial clone also needs local dependencies, datasets and runtime described in README.

## Git, secret and generated-file safety

- Never automatically run destructive commands such as `git reset --hard`, `git clean -fd`, `git restore .`, `git checkout -- .` or `git push --force`.
- Never discard local user changes without explicit authorization. Preserve remote history.
- Never commit or document passwords, API keys, tokens, personal access tokens, private keys, credentials, database passwords, private certificates or secret connection strings. Review suspicious configuration before staging; report findings without exposing values.
- Before committing, evaluate datasets, CSV/Parquet, ZIP archives, database dumps, binaries, model files, build output, caches, notebook checkpoints and generated output against .gitignore and repository policy.
- Keep raw datasets, runtime binaries, environments, caches and large generated outputs local. Small aggregate CSV/JSON reports and saved notebook outputs are intentionally tracked. Review size/content rather than treating every CSV/output as forbidden. Do not introduce Git LFS without demonstrated need.

## Project conventions

- Python 3.11, PySpark 4.0.4, Java 17, pandas and NetworkX; local Windows prototype.
- Run notebooks 01 → 02 → 03. Keep raw data unchanged. Keep inputs, staging and outputs within the local project; no Colab/Google Drive.
- Use BDA_PROJECT_DIR on another computer when needed. It defaults to root when opened from root or notebooks/.
- Read notebooks/README.md for label defaults, aggregate-before-join rules, hash split and threshold choices; do not change them silently.
- Distinguish observations from proposals: warehouse is conceptual; NetworkX is not a graph database; reviews text/JSON audit is not a document store; local Spark does not prove cluster scalability.
- Student fills the AI declaration. Do not choose its percentage or rewrite it without instruction.
- For documentation/configuration changes, check relevant static consistency and notebook schema/cell syntax where applicable. Run the pipeline when analytic logic changes and local prerequisites are available; record actual validation.
- Legacy maintenance scripts/exports/backups were removed. Use current notebooks and run_local_notebooks.py; do not recreate obsolete scripts as prerequisites.
