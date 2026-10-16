---
name: nt-debug-bug-codex
description: Use when investigating a bug from any source (Honeybadger fault, GitHub issue, PR comment, or plain description) to find the root cause through systematic analysis, reproduce it locally, fix, and verify.
---

# Debug Bug

Investigate a bug, find the root cause through systematic analysis, reproduce locally, fix, and verify. Works with any bug source: Honeybadger faults, GitHub issues, PR comments, or plain descriptions.

## Scope and authorization

When this skill supports [address-this-issue](../address-this-issue/SKILL.md), follow that workflow's scope, browser, verification, and cleanup rules first. Existing session authorization remains valid. A request to investigate does not authorize publication or production access.

The environment-discovery and data-verification steps below apply only to resources authorized in the current session. Authentication does not authorize reading credentials, deployment logs, or production databases. Request approval before accessing the needed NeetoDeploy logs. Production database access requires separate explicit authorization. Continue independent local investigation while access is pending or unavailable.

## Before you start

1. If the repo has an `LLM.md` at the root, read it before starting investigation. It captures product context (architecture, gotchas, local setup) that may inform the investigation. `CLAUDE.md` and `AGENTS.md` are auto-loaded by the harness, but `LLM.md` is not — read it explicitly. Apply its guidance throughout the entire process.

2. **Check what information is already available.** Throughout this skill, wherever it says "ask the user," first check whether that information was already provided in the initial prompt, LLM.md, or through available tools (MCP servers, database access, etc.). If the answer is already known, proceed without asking. Never skip an investigation **step** because of this. Only skip the **question** when you already have the answer. For example: if the initial prompt already includes error data, repo paths, and a GitHub issue link, do not ask the user for these again.

## Input

The skill works with whatever context is available. The chain below gathers as much as possible before investigation begins.

### Step A: Gather context

The user is expected to provide ONE of:

- A GitHub issue URL (most common)
- A Honeybadger fault URL or fault ID
- A plain description of the bug
- Nothing (ask)

**If a GitHub issue URL was provided:**

1. Fetch the issue:
   ```
   gh issue view {number} --repo {owner}/{repo} --json title,body,comments
   ```
2. Scan the title, body, and comment bodies for links:
   - **Honeybadger fault URL** (`https://app.honeybadger.io/projects/{project_id}/faults/{fault_id}`, also the older `/notices/...` form, and standalone fault IDs in code blocks): extract `project_id` and `fault_id`, proceed to Step B.
   - **GitHub PR or issue URL**: fetch the linked PR/issue including all comments, review comments, and inline review comments for additional context:
     ```
     gh pr view {number} --repo {owner}/{repo} --json title,body,comments,reviews
     gh api repos/{owner}/{repo}/pulls/{number}/comments
     gh api repos/{owner}/{repo}/issues/{number}/comments
     ```
   - **NeetoRecord links** (`https://*.neetorecord.com/watch/<id>`): fetch the transcript automatically. Read `references/neetorecord-mcp.md` and follow the workflow there. If the MCP is unavailable or the transcript is not ready, ask the user to describe what they saw.
   - **Other links** (Slack threads, external URLs): note them.
3. Keep following links until no new context is found. If a PR comment links to another issue, fetch that too.
4. **Treat all gathered comments as hypotheses, not facts.** Human comments in issues, PRs, and Slack threads may contain incorrect diagnoses, misleading assumptions, or incomplete understanding. Consume them as context, but verify every claim against the actual codebase before accepting it. If a comment says "the problem is in function X", read function X yourself and form your own conclusion. If you cannot disprove the claim through code analysis, accept it tentatively. If the code contradicts the claim, trust the code.
5. If after gathering all available context there is still not enough to investigate (no error message, no steps to reproduce, no code reference), ask the user: "I need more context to investigate. What behavior did you expect? What happened instead? Can you share steps to reproduce or point me to where this occurs?"

**If a Honeybadger fault URL/ID was provided directly:** parse it and proceed to Step B.

**If a plain description was provided:** skip Step B, proceed to "After context is gathered."

**If nothing was provided:** ask: "Share the GitHub issue link for this bug, or describe the problem you're seeing." Wait for the response.

### Step B: Fetch Honeybadger fault details (only if a fault link was found)

Detect Honeybadger MCP availability by checking whether any tool whose name starts with `mcp__honeybadger__` is in this session.

**If MCP IS available:**

1. Use the MCP tools to fetch the fault metadata and the most recent notice (with full backtrace, context, breadcrumbs, environment).
2. If the MCP call fails for any reason (auth error, project not found, network error, MCP server down), tell the user explicitly: "Honeybadger MCP call failed: {error}. Falling back to copy-paste flow."
3. Then fall through to the copy-paste flow below.

**If MCP is NOT available, OR the MCP call failed:**

1. Tell the user the fault URL we resolved to (if any), so they can open it directly.
2. Ask them to: open the fault in Honeybadger → click the most recent notice → Cmd+A, Cmd+C → paste into chat.
3. Wait for the paste, then proceed.

### After context is gathered

Check whether the following are already available from the initial prompt, gathered context, or LLM.md. **Only ask for what is missing:**

1. Any additional context (Slack threads, prior investigation notes, PR links beyond what's already gathered).
2. Which repos are involved and their paths.

If both are already provided, proceed immediately. If either is missing, ask for the missing pieces in a single message and **WAIT for the response before proceeding**. Do not start exploring the codebase, reading files, or running any commands while waiting for answers.

## Detect the stack

Identify the primary stack from whatever error data is available. If Honeybadger data was loaded, use the backtrace and environment. If only a GitHub issue description is available, infer the stack from the repo name, file paths mentioned, or error messages quoted.

Read the matching sub-file(s) at `stacks/`.

| Signal                                                                                                                                                                                                            | Stack file to read         |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| File paths ending `.rb`, `[PROJECT_ROOT]/app/`, `[GEM_ROOT]/gems/`, Ruby exception classes (`StandardError`, `NoMethodError`, `ActiveRecord::*`), `honeybadger-ruby` client, or repo is a Rails app               | `stacks/rails-backend.md`  |
| URLs containing CDN domain or `/node_modules/`, browser User-Agent in environment section, `@honeybadger-io/react` client with browser context, or bug is about frontend UI behavior                              | `stacks/react-frontend.md` |
| Server-side `.js` files with high column numbers (minified), deployment hostnames matching `*-deployment-*`, `@honeybadger-io/react` or `@honeybadger-io/nextjs` client with NO browser User-Agent in environment | `stacks/nextjs-ssr.md`     |

If the error crosses boundaries (e.g., frontend gets 500 caused by backend API), read BOTH relevant stack files and investigate both sides.

If no signal matches clearly, check the repo structure (Gemfile → Rails, package.json with next → Next.js, package.json with react → React). If still unclear, ask the user which stack applies.

## Auto-discover environment

Before starting investigation, silently verify what resources are available. Do not ask the user unless something critical is missing.

1. **Sibling repos**: If LLM.md lists sibling repos, check `../` for them. If the error context implies a sibling repo (e.g., a frontend error referencing a backend API), check `../` for it too. If a needed repo is not found at the expected path, ask the user for the correct path.

2. **Product documentation**: Check if a `docs/` directory exists in the product repo. If it does, list the filenames. You will use this in Phase 2 to read any docs relevant to the error domain.

3. **Framework source**: Note the framework internals location from the stack sub-file's "Framework source" section. You will use it in Phase 2.2.

4. **NeetoDeploy access (logs + production database)**: These are core debugging tools — set them up early.

   Check if `~/.config/neetodeploy/auth.json` exists. If it does:
   - Read `references/neetodeploy-logs.md` — production and review app log fetching via API.
   - Check if `psql` is available (`command -v psql`). If yes, read `references/neetodeploy-db.md` — read-only production database access via the read replica.

   If the auth file does not exist, tell the user: "NeetoDeploy CLI session not found. Production logs and database access will not be available. Run `! neetodeploy login` to enable them." **Do not stop the investigation** — continue without them, but note that production data verification will fall back to local DB or manual queries.

   **Always prefer querying the production database over the local database.** The local DB contains seed data, not real production state. Only fall back to local DB queries when production DB access is unavailable.

5. **Local database (fallback)**: Only if production DB access is unavailable (item 4). If the stack sub-file has a "Database type check" technique, run it now to determine whether the local database contains production data or just seeds. Note the result silently. Do not use `mise exec -- rails runner` or local DB queries when production DB access is available — production data is always more reliable.

6. **Dependency versions**: If Honeybadger data is available, compare local dependency versions against what the backtrace reports. The backtrace shows exact versions (e.g., `[GEM_ROOT]/gems/package-name-1.2.3/`). Run the equivalent local check (e.g., `bundle show <gem>` for Ruby, check `node_modules/<pkg>/package.json` for JS). If versions differ, local reproduction may hit different bugs than production. Flag any discrepancies and treat local reproduction results with additional skepticism — always validate against the production breadcrumbs.

## Phase 1: Map the error

### 1.1 Locate the crash site

If Honeybadger data is available, apply the **Backtrace reading** technique from the stack sub-file. The goal is to find the exact source file and line where the crash occurs.

If no backtrace is available (manual bug report), use the bug description to locate the relevant code. Search for the feature, endpoint, or UI component mentioned in the report. Read the code and understand the flow.

If the backtrace points to compiled or minified code, the stack sub-file describes how to map it back to source. If the backtrace points to source code directly, read the file at the specified line with surrounding context.

### 1.2 Identify the failing operation

Find the exact operation that fails. For example:

- `Cannot read properties of null (reading 'split')` means `.split()` is called on `null`
- `NoMethodError: undefined method 'foo' for nil:NilClass` means `.foo` is called on `nil`
- `ActiveRecord::RecordNotFound` means a query returned no results
- `StandardError` with a custom message means application code explicitly raised

For manual bug reports without an error message, identify the operation that produces the wrong behavior. What should happen vs what actually happens?

Search the crash site for ALL calls to that operation (e.g., every `.split()` call), not just the obvious one. In compiled/minified code, the crash site may contain code from multiple source files bundled together.

If the crash site is a deliberate `Honeybadger.notify()` call (not an unhandled exception bubbling up), this notice is a **secondary report**. The primary error was caught somewhere upstream. Investigate:

- What code catches the original exception? Does it re-raise, swallow it, or report it separately?
- Is there a **separate** Honeybadger fault for the original exception? Ask the user to check related faults on the same project around the same timestamp.
- If the original error is swallowed (e.g., caught, logged, but not re-raised), the breadcrumbs and surrounding code are your only evidence of the real failure.

### 1.3 Trace every context field

**This is the most important step when Honeybadger data is available. Do not skip or rush it.**

For EACH field in the Honeybadger context object, answer:

- What code sets this value? (Find the exact file:line that populates this context field)
- When is it set? (On every request? Only on errors? Does it persist across requests?)
- Is this from the crashing request or from a previous request?

Present findings in a table:

```
| Context field  | Value                          | Set by                        | Same request? |
|----------------|--------------------------------|-------------------------------|---------------|
| field_name     | value_from_context             | path/to/file.rb:47            | Yes / No      |
```

If a context field appears unrelated to the crash, that is a signal to investigate harder, not to dismiss it. Ask: "What sequence of events would cause THIS context to appear alongside THIS crash?"

For manual bug reports without Honeybadger context, skip this step.

## Phase 2: Investigate triggers

### 2.0 Check product documentation

If a `docs/` directory exists in the product repo (discovered in "Auto-discover environment"), scan the filenames. If any doc appears relevant to the error domain (e.g., an error in payment processing → read `stripe_integration.md`, an error in calendar sync → read `google_calendar_integration.md`), read it before proceeding. Domain documentation often explains integration flows, edge cases, and architectural decisions that are not visible from the code alone.

This directory may not exist in all products. If absent, skip this step.

### 2.1 Check application code

Read the source code at the crash site. Identify all inputs that could be null/nil/undefined. For each input, trace backward: where does it come from? What code path could make it null?

Apply the **Investigation techniques** from the stack sub-file for stack-specific patterns to check (e.g., default scopes in Rails, missing headers in Next.js, browser quirks in React).

### 2.2 Check framework internals

**Do not skip this step.** Many production errors come from how the framework processes requests internally, not from application code.

Apply the **Framework source** technique from the stack sub-file to locate and search framework internals.

Key question: "Does the framework ever invoke my application code with a request that is missing data my code assumes is present?"

### 2.3 Check previous fix attempts

If the user provided commit SHAs, PR URLs, or issue links, always use `gh` to fetch the full details. Do not rely on just the URL or title.

```bash
# Fetch PR state, diff, comments, and review comments
gh pr view <number> --repo <owner>/<repo> --json state,title,body,comments,reviews
gh pr diff <number> --repo <owner>/<repo>

# Fetch issue details and timeline
gh api repos/<owner>/<repo>/issues/<number>
gh api repos/<owner>/<repo>/issues/<number>/timeline --paginate
```

For each prior attempt:

1. Fetch the full PR/commit details using `gh`.
2. Read the diff to understand the code changes.
3. Read all comments to understand why the approach was chosen or abandoned.
4. Identify the assumptions behind each attempt.
5. Test whether those assumptions are correct.

A prior fix that was abandoned often contains a correct solution that was discarded for the wrong reasons.

## Phase 3: Reproduce locally

Apply the **Reproduction** technique from the stack sub-file for stack-specific reproduction approaches.

If the fix is obvious from code reading alone and does not require reproduction, skip this phase — but state why you are skipping it.

If reproduction requires a running server, check whether the server is already available (e.g., LLM.md specifies a running instance, or you can verify a local server is responding). If not, ask the user to start it and **wait for confirmation before sending any requests**.

### 3.1 Build a reproduction for each hypothesis

For each potential trigger identified in Phase 2, create a specific test using the technique from the stack sub-file.

### 3.2 Confirm the exact error

The local reproduction must produce the SAME error message and stack trace as production (when available). If it produces a different error, it is a different bug.

Check both:

- The HTTP response (status code, body) or job output
- The server/worker terminal output (error message, stack trace)

**If Honeybadger data is available, also compare the breadcrumb sequence.** Breadcrumbs record the operations that occurred before the error. If production breadcrumbs show operations A → B → C → D → failure, but your local reproduction fails at step B, you are reproducing a **different** error — even if the final error message is the same. This commonly happens when:

- A wrapper catches errors from multiple code paths and reports them with the same message
- Local dependency versions differ from production, causing a different code path to fail first
- Local data differs from production, causing a different record to trigger the error

### 3.3 Find ALL triggers

After reproducing the error one way, go back to Phase 2 and check if other triggers exist. A single error can have multiple causes. Common categories:

- **Direct triggers**: Bad input from external clients (bots, scanners, malformed requests)
- **Framework triggers**: Internal requests from the framework itself (optimizers, revalidation, prefetching, callbacks)
- **Data triggers**: Specific database records that cause code paths to fail (deactivated accounts, deleted records, nil associations)

Do not stop at the first reproduction. If Honeybadger context is available, it often describes a different trigger than the one you found first.

### 3.4 Verify data claims

If the error context references specific records (domains, organizations, users), you need to verify their state. Check in this order:

1. **Production database (preferred)**: If production DB access is available (discovered in "Auto-discover environment" item 4), query the read replica directly using `psql` and the instructions in `references/neetodeploy-db.md`. This gives you the actual production state. Do not use `mise exec -- rails runner` or local DB queries when this is available.
2. **Local database (fallback)**: Only if production DB is not available. Query the local DB using the technique from the stack sub-file. Use the database type check result from "Auto-discover environment" to judge whether the data reflects production state or just seeds.
3. **Ask for help**: If neither is available, ask the user: "The error references [specific record]. I need to verify its state. Could you run the following in production Rails console and share the output?" Then list the specific commands needed.

## Phase 4: Fix

### 4.1 Choose the right fix

The fix must handle ALL identified triggers, not just the first one you reproduced.

Apply the **Fix considerations** from the stack sub-file for stack-specific guidance on choosing the right fix approach.

### 4.2 Audit blast radius of structural root causes

**Do not skip this step.** If the root cause is **structural** — a missing association, a missing database constraint option, a missing dependent handling, a missing validation, or an unconfigured model — then the error is just one code path that exposed the gap. The same gap affects every code path that touches the same models.

Before implementing:

1. **Search for all code paths that delete or modify the affected models.** Search controllers, services, jobs, and rake tasks for destroy, delete, and delete_all operations on the affected model.
2. **Check both sides of the relationship.** If you are adding an association to one model, check whether the other model also needs a corresponding association or dependent handling. A structural fix that only addresses one side is incomplete.
3. **For each code path found, verify whether it would hit the same issue.** Test or reason about whether the same constraint violation or error would occur through that path.

Add any newly discovered triggers to your trigger list before implementing.

### 4.3 Implement

Make the smallest change that addresses the root cause. Do not refactor surrounding code.

### 4.4 Verify against ALL triggers

Rebuild and test against every trigger identified in Phase 3 and Phase 4.2:

```
| Trigger                          | Before fix | After fix | Pass? |
|----------------------------------|------------|-----------|-------|
| [trigger description]            | [error]    | [result]  | Yes   |
```

If the fix breaks any normal functionality (especially the scenario described in the bug report context), reconsider the approach.

### 4.5 Present results and wait for approval

After verifying the fix against all triggers, present the full summary (see Output below). When drafting the commit message, explain the root cause, not just the symptom.

If LLM.md authorizes autonomous commits or PRs, proceed with committing, pushing the branch, and creating the PR. Otherwise, ask the user to review the changes and give explicit approval before committing or pushing.

## Common traps

These are patterns that led to wrong conclusions in past debugging sessions. Watch for them. The stack sub-files contain additional stack-specific traps.

### Trap: Dismissing context fields as "stale" or "unrelated"

When Honeybadger context is available: the context may contain data from a previous request (e.g., set by an error interceptor or a before-action hook). But the CONTENT of that stale data is still a clue. If the context mentions an image URL, ask: "What code path involves images AND could trigger this crash?" Do not dismiss it as noise.

### Trap: Stopping at the first reproduction

Reproducing the error one way does not mean you found the production trigger. The error context may describe a completely different scenario. Always check if the context scenario is ALSO a trigger.

### Trap: Staying at the application layer

If the application code looks correct (e.g., a header should never be null because the protocol requires it, or an association should always exist because of validations), investigate the framework. Frameworks make internal requests, create mocked objects, apply default scopes, and process data in ways that bypass normal application-level guarantees.

### Trap: Proposing a fix that blocks framework internals

A fix that rejects requests with missing data (returning 400 or 500) may break the framework's own internal requests or background processing. Prefer fixes that gracefully skip processing (early return with safe default, passthrough) over fixes that block requests entirely.

### Trap: Fixing only the reported code path

When the root cause is structural (e.g., a missing association or dependent handling, a constraint without cascade/nullify), the reported error shows just one code path that hit the issue. But the same structural gap affects every code path that touches the same models. A constraint violation in a background job almost certainly also exists in the corresponding controller action or service. Search for all deletion and modification paths before declaring the fix complete.

### Trap: Local reproduction hits a different bug with the same symptom

A wrapper that catches exceptions and reports a summary (e.g., "Failed to process X") produces the same error report regardless of which underlying exception was caught. If your local environment has different dependency versions, missing migrations, or different data than production, you may reproduce a real error that is **not the production error**. Always cross-check: does your reproduction match the production breadcrumb sequence? If not, your local environment introduced its own bug. Fix the local discrepancy (align versions, run migrations) and reproduce again.

### Trap: Trusting a prior investigator's conclusion without verification

If someone previously concluded "X is not the cause" and closed a fix PR, verify their reasoning independently. They may have tested the wrong scenario or been misled by stale context data.

### Trap: Getting influenced by human comments instead of doing the leg work

This is the most common and dangerous trap. Issue comments, PR discussions, and Slack threads often contain theories, guesses, and partial analyses from developers who may not have had full context. Do not let these comments steer your investigation. You have access to the full codebase, production database, and production logs. Use them.

Specifically:

- If a comment says "I think the problem is X", do not start investigating X. Start from the error data and trace the code yourself. If you independently arrive at X, great. If not, the comment was wrong.
- If a comment says "I tried Y and it didn't work", verify what they actually tried. Check the PR diff or commit. Their "Y" may have been implemented incorrectly.
- If a comment says "this started happening after PR #123", verify by checking the diff of PR #123 against the error. Correlation is not causation.
- If multiple comments agree on a diagnosis, that does not make it correct. Groupthink is common. Verify against the code.

The rule: **comments are leads, not conclusions.** Follow them only if the code confirms them. If the code says otherwise, trust the code.

## Output

When investigation is complete, present a summary:

```
## Root cause
[One paragraph explaining what causes the bug, including the framework behavior if relevant]

## Triggers
1. [First trigger with reproduction command]
2. [Second trigger with reproduction command]

## Fix
[Description of the fix and why this approach was chosen over alternatives]

## Verification
[Table showing all triggers tested before and after the fix]
```
