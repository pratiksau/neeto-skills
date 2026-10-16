# Runtime Evidence and Session Cleanup

Read this reference when testing hypotheses with instrumentation, executing debugging runs, or removing task instrumentation. Use it with [debug-agent](../../debug-agent/SKILL.md). Apply the parent skill's scope and approval boundaries throughout.

## Start logging before instrumentation

Start the background logging server specified by `debug-agent` before adding instrumentation. It must remain available during the session without blocking the workflow. Capture its session ID, endpoint, port, and log path; read the documented format and choose the language's logging method.

If the server cannot start or no valid configuration is available, do not add instrumentation. Report the blocker and continue independent source analysis. Do not treat missing runtime evidence as confirmation.

The server can return an existing process. Record whether this task started it; do not stop a pre-existing server. Confirm that the session is dedicated to this task before writing or clearing logs. If session isolation cannot be established, report the blocker and continue work that does not affect another session.

Use NDJSON, one JSON object per line. Limit logging to the current session, exclude secrets and personal data, and include the fields needed to associate evidence with a hypothesis and run:

```text
sessionId, runId, hypothesisId, location, message, data, timestamp
```

Use the language-appropriate logging and region markers documented by `debug-agent`. Keep an inventory of this task's inserted markers and processes so cleanup can distinguish them from existing instrumentation.

## Execute and inspect runs

Use [@Browser](plugin://browser@openai-bundled), the in-app browser, to reproduce the bug yourself whenever possible. Check the fix yourself through the same browser flow whenever possible. Treat your own observed results and runtime evidence as confirmation. These automated runs replace `debug-agent` steps that require manual reproduction or repeated confirmation from the user; do not ask the user to repeat a check you can execute and inspect yourself.

Ask only for missing access or necessary human actions that the work actually requires. Continue independent investigation while waiting. Honor any prohibition on browser use or code changes.

For each run:

1. Associate each log entry with a hypothesis and run.
2. Confirm that the app loads the changed source and that the instrumentation executes.
3. Execute and inspect the affected flow, then read its logs.
4. Preserve relevant evidence before clearing logs. Save the entries or record the entries supporting conclusions, with references to them.
5. Between runs, clear only this task's dedicated session logs.

If no dedicated deletion tool is available, use the server's documented `DELETE /ingest/:sessionId` endpoint. Do not clear another session's logs. Clearing logs does not mean removing code instrumentation.

Compare before and after entries with interface and persisted state. Classify hypotheses as confirmed, rejected, or inconclusive using both entries and current code. Remove speculative fix changes for rejected hypotheses without reverting unrelated work. Keep instrumentation active for the first post-fix check.

Empty or missing logs require checking source loading, instrumentation execution, and reproduction conditions. They are not proof of a cause or successful fix. If runtime access remains unavailable, report unresolved hypotheses and continue source analysis.

## Cleanup after observed success

Once post-fix logs and observed behavior establish success, remove instrumentation without requiring an additional user confirmation when you performed and inspected the checks yourself. Explicit user requests to remove instrumentation also apply, but do not establish verification.

1. Remove only instrumentation inserted for this task.
2. Stop only debugging processes started by this task.
3. Search for this task's remaining instrumentation markers. Preserve existing instrumentation and other sessions' logs.
4. Inspect the final code differences.
5. Repeat the affected flow without instrumentation.

The fix must work without logging side effects. If checks fail or cannot run, report that limitation and continue authorized investigation; do not claim completion based on cleanup alone.
