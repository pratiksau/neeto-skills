# NeetoDeploy log access

Existing authentication does not authorize log access. Before reading credentials or fetching logs, check whether the current session authorizes the specific environment, application, process, time range, and purpose. Otherwise explain the needed logs, request approval, and wait. Continue independent local investigation.

Use the recipient's configured NeetoDeploy integration or CLI and its current documentation. This bundle does not provide credentials, deployment identifiers, or a log API configuration. Do not guess endpoints or use another person's session.

After authorization:

1. Confirm the target application and production or review environment.
2. Use the documented log command or API. Restrict the process, time range, and search to the investigation.
3. Inspect pagination when the relevant window spans more than one page.
4. Compare timestamps, request identifiers, exceptions, and job context with the reported failure.
5. Record which environment and interval the evidence covers. Exclude credentials and personal data from shared reports.

Do not upgrade the CLI, change deployment configuration, or deploy an application just to retrieve logs. Log approval does not authorize production database access.

If the integration, documentation, or access is unavailable, report the concrete gap and continue local investigation. Missing logs do not prove the absence of an error.
