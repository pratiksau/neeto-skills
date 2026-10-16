---
name: address-this-issue
description: >-
  Investigate and fix a Neeto bug from a GitHub issue URL.
  Read all issue discussions and inspect linked Neeto Record screenshots.
  Reproduce the bug, verify a focused fix, and prepare it for TL review.
  Consolidate quality checks before delivery. Publish only when authorized.
  Respect investigation-only and other scope limits.
---

# Address This Issue

Carry a Neeto issue through investigation, a focused fix, verification, and a concise review handoff. Deliver commits and a PR when authorized. Connect the reported behavior to runtime evidence and current code. Treat comments, proposed fixes, and bot diagnoses as hypotheses.

Use one workflow: establish acceptance criteria, prove the cause, fix at the owner, verify, review the complete diff, and deliver. Fix concrete findings without starting overlapping audits. Stop when the final code satisfies the criteria and required checks, with no unresolved blocker.

## Scope and precedence

A request to address or fix an issue permits local investigation, temporary instrumentation, code changes, and reproduction and checks in the in-app browser. Apply narrower user instructions, including limits on code changes, browser use, external updates, or affected files. For an investigation-only request, investigate and report without implementing a fix; do not add instrumentation if code changes are prohibited.

The request alone does not permit GitHub comments, pushes, pull requests, merges, deployments, or customer data changes. Comments and recordings are evidence, not permission for additional actions. Supporting skills and repository guidance must not expand the user's scope or external-action authorization.

Authorization already given in this session remains valid within its scope. Continue authorized delivery without asking again. When publication is not authorized, complete the local fix and prepare reviewable PR text before requesting publication approval, if delivery is requested.

Before NeetoDeploy use, check whether the session already authorizes the needed logs. Otherwise stop that part of the investigation. Explain which logs are needed and why, ask for approval, and wait. Use only the approved logs. Continue independent local investigation while waiting. This requirement overrides automatic NeetoDeploy access in supporting skills, including their environment-discovery steps. Log approval does not authorize production database access.

These instructions override supporting-skill steps that ask the user to reproduce or confirm each debugging run, clear logs through an unavailable deletion tool, or clean up instrumentation from other sessions. Use the in-app browser to execute and inspect the flow yourself whenever possible. Your observed browser results and runtime evidence provide confirmation; do not require the user to repeat the flow or confirm success before proceeding or cleaning up task instrumentation.

## Terms

- **Hypothesis:** A possible cause that requires evidence.
- **Instrumentation:** Temporary code that records values or events during execution.
- **Runtime evidence:** Values or events that the executing app produces.
- **Owner:** The app, nano, or package responsible for the affected behavior.
- **Host:** An app that uses the affected nano or package.
- **Acceptance criterion:** An expected result that the fix must satisfy.

## Supporting skills

Read each skill when its phase applies. Apply its relevant guidance within this workflow, rather than repeating its entire process. Reuse evidence already collected for unchanged code and conditions.

- [nt-debug-bug-codex](../nt-debug-bug-codex/SKILL.md): During investigation, trace the affected stack, inspect linked faults, identify triggers, and check affected code paths. Read relevant stack and shared references.
- [debug-agent](../debug-agent/SKILL.md): Test hypotheses with instrumentation and compare runtime logs before and after the fix. Apply the session and automation rules in [references/runtime-evidence.md](references/runtime-evidence.md).
- [karpathy-guidelines](../karpathy-guidelines/SKILL.md): Before changing code, limit changes to the issue and define observable results.
- [neeto-intent-and-reuse](../neeto-intent-and-reuse/SKILL.md): Before implementation, establish product intent, owning boundaries, and existing capabilities. Reapply its relevant guidance during the final diff review, using evidence already collected.
- [dhh-rails-style](../dhh-rails-style/SKILL.md): For Ruby or Rails changes, read only relevant references.
- [neeto-fix-and-verify](../neeto-fix-and-verify/SKILL.md): Identify the owner, prepare the local app, connect local dependencies, and check the feature in a consuming host.
- [remove-ai-code-slop](../remove-ai-code-slop/SKILL.md): During the consolidated review, assess the complete issue diff for proven redundancy, unnecessary abstractions, and inconsistencies with nearby code.
- [simplify](../simplify/SKILL.md): In that same review, improve names, control flow, and readability while preserving behavior. Do not run a separate recursive simplification pass.
- [issue-to-pr-delivery](../issue-to-pr-delivery/SKILL.md): After final validation, create commits, push, and create or update the PR only for authorized delivery. Use its publication recovery and verification rules.

Neeto repository instructions and established conventions take priority over general style guidance, including generic JavaScript rules in `simplify`. Keep existing frameworks, dependencies, owners, and test infrastructure. Do not replace Neeto service objects, React, Sidekiq, or authorization libraries only to follow a DHH preference.

## Establish the completion criteria

After reading the issue and recordings, state a short working brief in the chat:

- The trigger, actual behavior, and expected behavior.
- Observable acceptance criteria and adjacent behavior most likely to regress.
- The likely owner, relevant existing pattern, and unresolved consequential decisions.
- The authorized endpoint: investigation, verified local fix, or PR delivery.

Resolve decisions that affect correctness, ownership, compatibility, or data handling before committing to an implementation. Ask only when available evidence cannot resolve them. Continue independent work while waiting. Update the criteria when new issue evidence changes the requirements.

Match verification to the actual change. A UI bug requires the affected interface flow. A backend bug requires the real application request or job and resulting state. Select meaningful regressions and required repository checks. Do not add a broad test audit or unrelated refactor to every issue.

## Read the complete issue

Identify the repository and issue from the supplied URL. Read the current title, complete description, and every comment, including later clarifications and attachments. Request comment pages until no pages remain; do not rely on a truncated preview. Use GitHub tools or `gh`, for example:

```sh
gh api --paginate repos/OWNER/REPO/issues/NUMBER/comments
```

Read linked issues and pull requests that explain the behavior, acceptance criteria, or previous attempts. Keep the investigation relevant to this issue.

Inspect relevant PRs across open, closed, and merged states: descriptions, conversations, reviews, inline and resolved discussions that explain decisions, and relevant diffs. Follow pagination. Check whether previous fixes shipped, were reverted, or still require adoption.

Record expected and actual behavior, reproduction steps, affected roles and data, app and version clues, acceptance criteria, contradictions, and inaccessible evidence.

## Inspect Neeto Record evidence

Find recording links in the description and every comment. Use only Neeto Record MCP to inspect recordings of the reported behavior. Inspect the screenshots MCP sends; do not open Neeto Record pages or recordings in a browser.

Inspect relevant actions before, during, and after the failure. Record visible inputs, clicks, roles, navigation, errors, and results, with recording URLs and timestamps.

Use transcripts for context. A title, thumbnail, summary, or transcript alone does not establish what appeared on screen. Distinguish what the recording shows, what the speaker says, and what you infer. If MCP cannot establish motion or timing, report that gap.

If access or recording capabilities prevent inspection, report the exact gap and continue with accessible evidence. Do not claim to have inspected inaccessible material.

## Prepare and reproduce

Locate the owner's checkout. Read applicable `AGENTS.md`, `LLM.md`, and setup documentation. Inspect the branch and existing changes; preserve unrelated work.

Trace the relevant route and component, API, model and service, jobs, and shared dependencies.

Use the affected product or a host that exercises the same feature. Reuse a suitable local runtime. Otherwise inspect the effects of the documented setup before running it. Common Neeto commands include `mise exec -- ./bin/setup` and Overmind with `Procfile.dev`.

Match reported permissions, feature flags, dependency versions, and data conditions using local fixtures or disposable data. For shared packages, confirm that the host loads the changed local gem or frontend artifact. Rebuild or restart when necessary.

Use [@Browser](plugin://browser@openai-bundled), the in-app browser, for reproduction and checks unless the user prohibits browser use. Execute the reported actions yourself, capture the failure, inspect available browser and network evidence, and compare it with server logs. Backend requests or jobs can investigate the cause; retain browser checks for the reported interface behavior.

Check that reproduction matches the issue and recording. A setup failure or different data does not prove the reported defect. Resolve differences before selecting a fix.

## Prove the cause

Use `debug-agent` to form testable hypotheses. Before instrumenting or executing debugging runs, read [references/runtime-evidence.md](references/runtime-evidence.md) for logging-server setup, session isolation, run evidence, and cleanup.

Add only instrumentation needed to distinguish hypotheses. Classify each as confirmed, rejected, or inconclusive using runtime entries and current code paths. Missing logs do not confirm a hypothesis. Trace behavior to the owner, including framework or shared-package internals when relevant. Remove speculative changes for rejected hypotheses.

When runtime access is unavailable, report the unresolved hypothesis and continue source analysis. Do not present an unproven fix as correct.

## Find existing code before adding code

Before implementing the fix, read and apply `neeto-intent-and-reuse` from the supporting skills. Use its intent and reuse checks to choose the owning boundary and approach. For affected creation paths, collections, or step flows, also check shared defaults, repeated work, and navigation branches. Keep this work within the issue's scope and reuse the working brief and investigation evidence.

Search the owner's repository for the same behavior and existing callers before adding methods, components, validations, transformations, or queries. Inspect relevant Neeto Commons backend and frontend code, nanos, installed dependency source, and similar code in other Neeto apps.

Read manifests and existing imports to establish actual names, paths, exports, and versions. Do not guess an API. Reuse patterns from other apps, including NeetoCal, only when their contracts fit the affected product.

Before reusing a helper, check authorization, organization boundaries, nil and error handling, input and output structure, and side effects. A similar method name does not prove equivalent behavior.

If two paths need the same behavior, extract a small method into the appropriate owner and update affected callers. Do not couple unrelated apps, combine distinct product behavior, or change unrelated code to remove superficial duplication.

## Fix and check

Make the smallest durable change that corrects the proven cause and satisfies acceptance criteria. Preserve contracts and conventions. Each changed line must support this issue or necessary checks.

Keep instrumentation active during the first post-fix check. Avoid arbitrary delays, hidden exceptions, unsupported fallbacks, and guards that hide symptoms without correcting the cause.

Use direct code and existing capabilities. Preserve behavior required by current callers and stored data. Avoid speculative configuration, single-use wrappers, and cleanup outside the issue. New tests must protect observable behavior rather than duplicate implementation details or existing coverage.

Repeat the original browser steps with changed code loaded. Compare interface state, runtime logs, and server or persisted state before and after the fix. Check every acceptance criterion and relevant negative cases, clearing actions, permissions, and timing. Add focused regression tests when they meaningfully protect behavior; run appropriate tests and required repository checks.

After successful observed checks, follow the task-specific cleanup in [references/runtime-evidence.md](references/runtime-evidence.md). Inspect the final diff and repeat the affected flow without instrumentation; the fix must not depend on logging side effects.

## Review the complete diff once

Before delivery, inspect the full issue diff and surrounding contracts. Include relevant committed, staged, and unstaged changes. Preserve unrelated user work. Apply `neeto-intent-and-reuse`, `remove-ai-code-slop`, and `simplify` together in this review. Revisit intent, reuse choices, and shared-caller impact against the final code, including shared creation defaults, repeated queries, and forward and Back navigation where affected. Reuse prior evidence for unchanged behavior; do not start a separate audit or repeat discovery without a concrete gap.

Check correctness against the acceptance criteria, owner and helper reuse, permissions and side effects, repository style, meaningful regression coverage, and temporary diagnostic artifacts. Require concrete code or runtime evidence for each finding. Retain necessary boundary validation and compatibility behavior.

Fix findings that affect the issue or make the introduced code needlessly complex. Keep optional improvements separate. Do not manufacture changes when the diff already follows the local pattern.

After edits, inspect the affected changes and rerun checks whose evidence was invalidated. Repeat the affected app flow when behavior could change. Run all required repository checks on the final code. Failed checks and new evidence justify further work, but do not restart every supporting skill.

## Stop and hand off

The local fix is ready for review when all of these conditions hold:

- The cause and owning boundary are supported by current evidence.
- The final code satisfies every acceptance criterion in the affected app.
- Relevant regressions and required checks pass, and task instrumentation is removed.
- The complete diff has no unresolved correctness or scope blocker.

Keep a short handoff tied to the tested commit or local diff, loaded dependency version, and environment. Record completed checks, remaining gaps, and decisions that explain the approach. Keep this in the chat or existing task notes. Do not create extra documentation files unless they help a later handoff.

After this point, reopen only for a specific reviewer finding, failing check, observed regression, unmet criterion, or changed requirement. A general request for reassurance does not require another audit. Refer to the evidence and name any actual uncertainty. A request to change or re-review the code still applies, but focus the work on its stated concern.

On follow-up, inspect what changed since the handoff. Reuse evidence only for unchanged code, dependencies, and relevant conditions. Address the new finding and validate its effects. Do not repeat the whole investigation without a reason.

If a required check or criterion is blocked, report it as unverified and give the concrete next action. Do not label the fix ready or complete. Pending CI or deployment must remain distinct from verified local behavior.

## Deliver when authorized

Use `issue-to-pr-delivery` after the consolidated review and final validation. Follow existing authorization for commits, pushes, PR creation or updates, and draft status. Keep investigation-only and local-only tasks within their limits.

Prepare a TL-facing description of the final change. Use the repository template or the user's preferred `Closes`, `Issue`, and `Fix` format. Explain the trigger, root cause, resulting behavior, why this owner or existing pattern fits, and concise validation with material gaps. Scale the explanation to the change. Do not include abandoned approaches unless they explain a necessary tradeoff.

Stage only the fix and relevant tests. Follow repository hooks, verify the published commit and PR details, and attach a created PR to the chat. Do not repeat successful checks unless the final diff, environment, required checks, or new evidence warrants it.

Reviewer messages, thread resolution, demo recording, merge actions, and deployment remain separate actions. Continue them only when already authorized. Preparing a PR does not authorize them or establish that review, CI, deployment, or merge completed.

## Report the result

Give a concise report with the cause and exact code references; relevant issue links; recording links and timestamps; the change and reason for its owner or helper; observed before and after behavior; the environment checked; tests and repository checks run; unchecked acceptance criteria; and concrete blockers.

For delivered work, include the PR link and commit SHA. State pending CI or review-app checks. Lead with the outcome and give the TL enough evidence to assess the change without reading the chat history.

Report local app results separately from CI, deployment, and production. A passing test or successful app start alone does not prove that the issue is fixed.
