---
name: remove-ai-code-slop
description: Review the current branch diff against main and remove AI-generated code slop while preserving intended behavior. Use when asked to clean up a branch, remove AI slop, simplify suspicious generated-looking changes, or align newly introduced code with surrounding repository style. Focus on unnecessary comments, abnormal defensive checks or exception handling, type-system bypasses such as casts to any, avoidable nesting, and other branch-introduced patterns inconsistent with nearby code.
---

# Remove AI Code Slop

Clean only branch-introduced code that is demonstrably inconsistent, redundant, or needlessly complex. Treat “AI-generated” as a cleanup heuristic, not an assertion about authorship.

## Establish scope

1. Read repository instructions before editing.
2. Inspect the worktree status and preserve unrelated user changes.
3. Resolve the comparison base. Prefer the current upstream default-branch ref such as `origin/main`; fall back to `main` only when necessary. State the chosen baseline if it may be stale or ambiguous.
4. Review both the complete diff from the merge base and the surrounding code. Use `git diff <base>...HEAD` for committed branch changes, then include relevant unstaged and staged changes when they are part of the requested work.
5. Exclude generated files, vendored code, lockfiles, and unrelated pre-existing changes unless the cleanup directly requires them.

## Evaluate before editing

Require concrete evidence from the file, nearby code, repository conventions, types, tests, or runtime contracts. Do not remove code merely because it is verbose or unfamiliar.

Look for branch-introduced instances of:

- Comments that restate the code, narrate obvious steps, or use a tone absent from the file.
- Defensive guards, fallback values, optional chaining, validation, or `try`/`catch` blocks that duplicate established guarantees or are abnormal on a trusted internal path.
- `any`, unsafe assertions, ignored type errors, or broad casts added only to silence the type checker.
- Deep nesting that can become clearer through a guard clause, early return, extraction, or simpler control flow.
- Thin wrappers, needless abstractions, duplicate helpers, speculative extensibility, verbose logging, or repeated transformations unsupported by local patterns.
- Formatting, naming, test structure, or error handling inconsistent with adjacent code.

Distinguish cleanup from behavior changes. Keep defensive handling at external or untrusted boundaries unless the repository contract proves it redundant. Fix a narrow underlying type mismatch when practical; never replace one unsafe cast with another or broaden types to hide an error.

## Make surgical changes

1. Edit only confirmed findings introduced by the branch.
2. Prefer the smallest change that restores the local pattern and leaves one clear source of truth.
3. Preserve public behavior, error semantics, data shape, ordering, and side effects unless the user explicitly requests a behavior change.
4. Avoid drive-by refactors, reformatting, dependency changes, and speculative improvements.
5. If a suspicious construct cannot be proven unnecessary, leave it in place and mention the uncertainty rather than guessing.

## Verify

1. Re-read the resulting diff against the selected baseline and confirm every edit belongs to the cleanup.
2. Run `git diff --check`.
3. Run the narrowest relevant formatter, linter, type check, and tests available for changed code. Follow repository-specific commands and execution wrappers.
4. Expand verification only when the risk or failure signal warrants it.
5. Confirm no unrelated user changes were overwritten and no unsafe type bypasses or debug artifacts remain in the cleaned diff.

## Report

Lead with the outcome. Summarize the concrete slop removed, identify the baseline, list verification performed and its result, and call out anything intentionally retained because evidence was insufficient. Do not claim code was AI-authored; describe the observable pattern instead.
