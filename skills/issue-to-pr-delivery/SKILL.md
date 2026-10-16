---
name: issue-to-pr-delivery
description: Turn validated local issue fixes into commits, pushed branches, and pull requests with concise issue-linked descriptions. Use when the user asks to deliver an existing fix, commit and push it, or create its PR. Investigation and merge work require separate scope.
---

# Issue-to-PR delivery

Deliver the existing fix with a focused commit and a PR that explains the issue and resulting behavior.
Use the current issue, final diff, and validation evidence as the source of truth.

## Establish the delivery scope

1. Read the current request and earlier instructions for the fix.
2. Identify the issue URL, repository, checkout, branch, remote, and intended base branch.
3. Read applicable repository instructions and its PR template.
4. Inspect staged, unstaged, and untracked files, plus existing commits and any PR for the branch.

Honor explicit limits such as local-only, no push, draft PR, or an empty PR description.
A request to commit, push, and create a PR authorizes those actions without another confirmation.
Automatic skill selection alone does not authorize publication.
If publication is not authorized, prepare the local diff and PR text before requesting the missing authorization.

Reuse the checkout and branch that contain the fix when suitable.
If isolation is necessary, preserve the validated changes when creating another branch or worktree.
Do not discard local work or move unrelated changes into the delivery.

## Check the final change

Compare the final diff with the issue and the recorded validation.
Identify what reproduced the issue, what passed after the fix, and what remains unchecked.
Earlier test results apply only to the code and environment that produced them.

Run required repository checks and checks needed for changes since validation.
Do not repeat completed checks without a reason.
Remove temporary diagnostic code introduced for this fix.
Keep temporary PR bodies, reply payloads, and demo artifacts outside the commit unless requested.

If browser QA is missing, say so.
Use browser access only when the user authorized it in the current workflow.
Do not substitute automated tests for a claim of browser reproduction or manual QA.
If a required check fails, address the relevant failure before publishing.
Report any blocker that cannot be resolved within scope.

## Write the commit and PR text

Read and apply both writing skills:

- [$asd-ste100](../asd-ste100/SKILL.md). Use STE-flavored mode for commit messages and PR prose.
- [$unslop](../unslop/SKILL.md). Remove filler and AI patterns while preserving facts and uncertainty.

Use a short title that names the corrected behavior.
Describe the final implementation for a reviewer who did not read the chat.
The user's preferred body contains a closing reference, an Issue section, and a Fix section.
Use this shape unless the user or repository requires another format:

```markdown
Closes #<issue-number>

## Issue

<Trigger and incorrect behavior. Mention persistence or affected modes when relevant.>

## Fix

<Change and resulting behavior. Include the mechanism only when it helps review.>

<Brief validation results and material limits, if relevant.>
```

Keep simple fixes to a few sentences.
Place brief validation under Fix instead of adding a long checklist by default.
Use a full issue URL for an issue in another repository.
Use a non-closing reference if the PR addresses only part of the issue.
Preserve an explicitly requested empty description.

Do not copy historical test counts, issue numbers, or claims of successful QA into a new PR.
Distinguish local validation from CI, review-app validation, and production evidence.
If the diff changes, revise the title and body to describe the final result.

## Commit and publish

1. Stage only the fix and its relevant tests.
2. Inspect the staged diff before committing.
3. Create a focused commit using the repository's normal hooks and pinned toolchain.
4. Inspect any changes made by hooks and resolve relevant failures without bypassing the hooks.
5. Push the intended branch to the intended remote.
6. Create the PR against the confirmed base, or update its existing PR when authorized.

Use GitHub CLI or an available GitHub connector.
With `gh`, specify the repository, head, and base explicitly.
Save multiline PR text to a temporary file and pass it through `--body-file`.
If publication times out, check the remote branch and PR before retrying.
Do not create a duplicate PR or force-push to recover from an uncertain result.

Verify the published commit, PR URL, head, base, and body.
Attach a created PR to the current Codex chat with `attach_artifact` when that tool is available.
Check the working tree for hook changes or unrelated files before reporting its state.

## Report the delivery

Return the PR link, commit SHA, relevant validation, and any material limit.
State whether CI or review-app checks are pending when known.
Do not claim that creating the PR completes its review, deployment, or merge.

Merge actions, `mergepr` labels, reviewer replies, thread resolution, and demo recordings require separate authorization.
Continue those actions when the user already included them in the task.
Do not add them merely because the PR exists.
