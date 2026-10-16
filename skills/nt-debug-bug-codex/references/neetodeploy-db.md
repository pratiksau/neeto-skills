# Production database evidence

Production database access requires explicit session authorization separate from log access. Authentication and an available CLI do not grant that authorization. Continue local investigation if production access is unavailable or outside scope.

Use the recipient's approved connection procedure and current deployment documentation. This bundle contains no database URLs or credentials. Do not fetch environment variables or connection secrets before authorization.

For an authorized inspection:

1. Confirm the application, environment, and approved read replica or read-only account.
2. Use a read-only transaction and a bounded statement timeout.
3. Select only the columns needed to establish the hypothesis. Limit returned rows.
4. Never run data changes, schema changes, state-changing functions, or external side effects.
5. Keep credentials and personal data out of tool output, commits, and shared reports.

Do not fall back to a writable primary database when a read replica is unavailable. Report the gap instead. Local fixtures and production records provide different evidence. State which one was inspected.
