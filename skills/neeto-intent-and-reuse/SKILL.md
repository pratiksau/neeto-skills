---
name: neeto-intent-and-reuse
description: Check product intent, existing implementations, and shared-path impact before implementing Neeto features or preparing their PRs. Use when a change adds a workflow, duplicates domain logic, or alters shared models, services, jobs, or nanos.
---

# Neeto intent and reuse

Make the implementation's purpose, reuse choices, and effect on existing callers clear before code review. Apply before editing and revisit against the final diff. Scale discovery to the change rather than auditing the whole ecosystem.

## Establish the intended behavior

Read the request, relevant issue discussion, linked recording when supplied, and applicable repository instructions. Identify the starting state, requested result, and content or relationships that must remain, change, or disappear. Distinguish a new workflow from an extension to an existing one.

State the intended behavior and proposed owning boundary in a short progress update before implementation. If two interpretations would produce different behavior, check available product evidence first. Ask only when a material decision remains unresolved, and continue work that does not depend on it.

An operation with a similar name is not sufficient evidence of equivalent behavior. For example, copying and moving can require different treatment of identity, history, archived content, and source removal.

## Inspect existing capabilities before designing

Use targeted searches to find the current entry point, domain models and methods, related services, callers, and tests. Search capabilities and accepted parameters, not only class names. Follow promising implementations far enough to understand their behavior and limitations.

Check installed dependency source and relevant shared owners, especially `neeto-commons-backend`, engines, and nanos, before writing a local replacement. If shared code owns the behavior, make the fix there rather than adding a host workaround. Inspect analogous NeetoCal or NeetoForm code when it helps establish a Neeto convention. Preserve the current product's requirements and stack.

For each plausible reuse candidate, establish what it preserves, omits, resets, or creates, and what assumptions its callers rely on. Reuse it when those semantics fit. When they do not, identify the specific difference before creating another path. Do not claim that no existing logic exists when a relevant capability was merely unsuitable or inaccessible.

Share overlapping invariants through an existing model, method, or package where possible. Extract a small helper only when concrete callers need the same behavior. Keep different lifecycle operations separate when combining them would change meaning. Matching users by email can be shared even when copying and moving require different record handling.

Before adding find-or-create or default-record initialization, search other creation paths, including automation and cloning. Compare attributes, defaults, resource types, and failure behavior. When callers need the same invariant, put it on the owning model or existing shared owner and update those callers together. Resolve differences against the intended contract rather than preserving accidental drift. Check both the existing-record and missing-record cases; do not turn a read-only accessor into a writer just to reuse it.

## Check repeated work and workflow transitions

For collection processing, inspect the actual request payload and the work each iteration triggers. Forms may submit every item, including empty selections. Skip items that require no action before querying or creating records, while preserving any clearing behavior an empty selection represents. Identify repeated lookups whose result stays constant during the operation and resolve them once or cache them within that operation. Estimate query growth with a representative collection size, and measure it when the cost is uncertain. Use existing bulk operations when they fit; avoid a broad batching rewrite without evidence that it is needed.

When adding, removing, or conditionally skipping a workflow step, trace forward, Back, and submission transitions for each affected branch. Back must return to the preceding applicable step, which may differ from the preceding numeric page. Check entry points and relevant conditions such as workspace ownership, permissions, and empty data. Verify that required controls remain reachable and that navigation preserves the expected selections. If a branch cannot be exercised, name that branch as unverified.

## Check the effect on other callers

When changing a shared path or default, inspect its relevant callers and alternate ways to perform the operation. These may include UI requests, external APIs, MCP tools, imports, jobs, automations, or conversions. Trace the paths that can exercise the changed invariant. Do not assume one controller or service covers every write.

Before adding locks or transactions, identify the rows they affect, the duration they are held, and the operations that will wait. Scope synchronization to the records or modes that require it. Account for counters, callbacks, rendering, and external I/O inside the transaction. Move work outside a transaction only when the resulting failure and side-effect semantics remain correct.

When writes can overlap an ownership change, coordinate the relevant writers and revalidate ownership after waiting. For database concurrency fixes, verify the relevant orderings with separate connections. A stale-object unit test alone does not prove that concurrent requests coordinate correctly. Keep ordinary workflows independent when only a special workflow requires coordination.

## Verify the chosen boundary

Use application behavior as the test contract. Protect relevant outcomes such as ownership, retained content, assignments, permissions, numbering, or completion notifications. Avoid assertions that only restate Rails behavior or implementation structure.

For a bug, demonstrate the failure before the fix when feasible, then verify the same case afterward. Extend existing coverage when it already owns the contract. Add another layer only for a distinct risk that the existing test cannot reach. Report unavailable evidence as unverified rather than compensating with speculative code.

Compare the final branch diff with the upstream default branch and include relevant local changes. Remove branch-introduced duplication, unnecessary wrappers, and unrelated edits. Confirm that each changed line supports the intended behavior or its verification. Run the relevant repository checks without repeating completed checks unless the code or evidence changed.

## Answer the design questions before PR review

Keep brief working notes during investigation. Do not create permanent design documents unless the task needs them. In the PR description or handoff, answer the questions that matter to this change:

- What user-visible result is required, and what must be preserved?
- Which existing implementation or shared capability was checked and reused?
- If a new path is needed, which specific requirement prevents direct reuse?
- How do shared callers and ordinary workflows behave after the change?
- For collection or step-flow changes, what repeated work is avoided and which navigation branches were checked?
- What verification proves the result, and what remains unverified?

Name relevant methods or files when they help a reviewer assess the decision. Keep the explanation proportional to the diff and honor the user's requested PR format. Avoid claiming that discovery alone proves correctness, that all paths were covered, or that the PR is ready to merge without supporting evidence.

This skill guides implementation and review preparation. It does not authorize commits, pushes, GitHub replies, thread resolution, deployment, or merging. Follow authorization already provided for the task.
