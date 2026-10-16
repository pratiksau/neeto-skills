---
name: neeto-fix-and-verify
description: Investigate and fix Neeto bugs using issue and PR discussions, existing Neeto coding conventions, and end-to-end verification in a real consuming app. Use for Neeto app, nano, or shared-package fixes and acceptance verification.
---

# Neeto Fix and Verify

Carry a Neeto code fix from evidence gathering through verification in a running application. Acceptance requires exercising the affected behavior in a real app such as neeto-cal or neeto-desk with the changed code loaded.

## Understand the full history

- Read the issue body, all issue discussion, and linked issues relevant to the reported behavior.
- Find related PRs across open, closed, and merged states. Read their descriptions, conversation comments, reviews, inline review discussions, and relevant diffs. Include resolved threads when they explain a decision; follow pagination rather than relying on a truncated preview.
- Determine why earlier PRs were closed, superseded, or reverted and which conclusions still apply to the current code. A closed PR is evidence, not proof that its implementation shipped.
- Extract concrete reproduction steps, expected behavior, and acceptance criteria. Treat bot findings and proposed fixes as hypotheses until checked against current callers, data contracts, and runtime behavior.
- If history is inaccessible, record the missing evidence instead of interpreting it as no discussion. Reading discussions does not authorize posting replies or resolving threads.

## Fix at the owning boundary

Inspect the owning app, nano, or package and its consumers before changing code. Keep reusable behavior in its shared owner and product-specific behavior in the host. Make the smallest durable change that addresses the causal defect.

Follow existing Neeto coding style. Inspect analogous code in `neeto-cal-web`, the usual Neeto code standard, and use its conventions where they fit the owning project's architecture and behavior. Preserve the current product's requirements and established stack.

- For Ruby or Rails work, use [dhh-rails-style](../dhh-rails-style/SKILL.md) and read the references relevant to the change. Apply clear Rails conventions without replacing existing dependencies, frontend frameworks, or test infrastructure merely for stylistic consistency.
- Use [build-simple-durable-systems](../build-simple-durable-systems/SKILL.md) whenever its guidance helps implementation, architecture, or dependency decisions. Prefer direct code and existing capabilities over speculative abstractions. If its guidance conflicts with required behavior or safe handling of existing data, state the conflict and prioritize the explicit requirement.

## Set up a real consuming app

Choose an app that actually exercises the affected feature. Prefer the user's specified app; otherwise use a suitable NeetoCal or NeetoDesk consumer. Testing an unrelated feature in a familiar app does not establish acceptance.

- Inspect the repository instructions, runtime versions, setup script, and `Procfile.dev` before starting processes. Neeto projects can generally be set up with `./bin/setup`; check what that script changes and use the repository's documented toolchain, including `mise exec -- ...` when needed.
- Run the app with Overmind, typically `overmind start -f Procfile.dev`, or start the Rails server and the other required processes individually using the commands in `Procfile.dev`. Include frontend builds and workers when the affected flow needs them.
- Reuse suitable running services and avoid port conflicts. Use local test data and credentials. Keep track of processes started for this task.
- For nano or package changes, use the repository's established local dependency-linking or build workflow. Verify that the host resolves the changed source or artifact, including the backend gem or frontend bundle as applicable. A running app using the old published version proves nothing about the fix.

## Acceptance through observed behavior

Reproduce the original failure in the running app before the fix when feasible, then repeat the same steps with the changed code loaded. For a UI defect, exercise the actual user flow in a browser when authorized. For backend behavior, drive the relevant real application request or job and inspect the resulting state or output. A direct helper call alone does not verify host integration.

Check each acceptance criterion and the adjacent behavior most likely to regress. Run focused automated regression coverage and required repository checks as appropriate. Unit tests, mocks, static inspection, server startup, and passing CI support the result; they do not replace exercising the affected flow in the real consuming app.

Mark a criterion verified only after observing its expected result. If credentials, setup, local dependency wiring, or another constraint prevents real-app testing, continue useful authorized work and report the criterion as unverified with the concrete blocker. Do not declare the fix complete or everything verified while an acceptance criterion remains untested.

Report the root cause and narrow change, issue and PR history that influenced it, app and code version tested, reproduction steps, observed before/after behavior, checks run, and remaining gaps. Distinguish local app evidence from staging or production evidence; local success does not establish release or deployment.
