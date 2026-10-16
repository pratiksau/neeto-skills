# Rails Backend Investigation Techniques

Techniques for debugging Honeybadger errors with Ruby backtraces — application code, gem code, Sidekiq workers, and Rails engine errors.

## 1. Backtrace reading

Rails backtraces show direct file:line references. Two path prefixes tell you where to look:

- **`[PROJECT_ROOT]/app/`** — Application code. Read the file directly at the line number shown.
- **`[GEM_ROOT]/gems/`** — Gem code (including nano engine gems). Find the gem source on disk:

```bash
mise exec -- bundle show <gem-name>
# Output: /path/to/gems/<gem-name>-<version>
# Then read: /path/to/gems/<gem-name>-<version>/<backtrace-file-path>
```

For nano gems (e.g., `neeto_*_nano`), the gem source is often available as a sibling repo at `../<nano-name>`. If the sibling repo exists, read from there instead of the installed gem — it may have newer code.

Read the backtrace top-to-bottom. The first frame is where the error was raised. Scan down for the transition from gem/framework code back into application code — that is often where the real problem is.

## 2. Framework source

Locate framework and gem internals for investigation:

```bash
# Find any gem's source location
mise exec -- bundle show sidekiq
mise exec -- bundle show activerecord
mise exec -- bundle show neeto_custom_domains_engine

# Then read/search the source at the returned path
```

Key framework locations to investigate:
- **Sidekiq**: `lib/sidekiq/processor.rb` (job execution), `lib/sidekiq/middleware/` (middleware chain)
- **ActiveRecord**: Callbacks, default scopes, association loading
- **Rack middleware**: Request processing chain, how headers/params are parsed
- **Rails engines**: Nano engines mount routes and add middleware — check their `lib/<engine>/engine.rb`

## 3. Investigation techniques

### Default scopes hiding records

A common Rails trap. A model with `default_scope { where(deactivated_at: nil) }` will silently exclude deactivated records from all queries. An association like `belongs_to :organization` returns `nil` if the org is deactivated — even though the record exists in the database.

Check for this pattern:
```bash
# Find default scopes in the project
grep -r "default_scope" app/models/ --include="*.rb"

# Verify a record exists but is hidden by scope
mise exec -- rails runner "
  record = ModelName.unscoped.find('id-from-context')
  puts record.inspect
  puts 'deactivated_at: ' + record.deactivated_at.to_s
"
```

### Nil associations

When a service object calls `record.association.method` and gets `NoMethodError: undefined method 'method' for nil:NilClass`, the association returned nil. Trace why:
- Is the foreign key present? (`record.association_id`)
- Does the associated record exist? (`AssociatedModel.unscoped.find(record.association_id)`)
- Is a default scope filtering it out?
- Was the associated record deleted?

### FK constraint audit

When an FK constraint causes a deletion failure, the constraint affects **every code path that deletes the referenced model** — not just the one that triggered the Honeybadger error. Run all three steps before implementing a fix.

**Step 1 — Find FK constraints on the affected tables:**
```bash
mise exec -- rails runner "
  tables = %w[table_a table_b table_c] # tables involved in the error
  tables.each do |t|
    ActiveRecord::Base.connection.foreign_keys(t).each do |fk|
      puts \"#{t}.#{fk.column} -> #{fk.to_table} (#{fk.on_delete || 'NO ACTION'})\"
    end
  end
"
```

Any FK with `NO ACTION` (no cascade/nullify) is a potential violation point. In batch deletion (e.g., incineration), it means the referencing table must be deleted first. The deletion order is typically derived from `belongs_to` declarations (via topological sort) — if the database FK exists but the model lacks the corresponding `belongs_to`, the sorter won't know about the dependency.

**Step 2 — Check the referenced model for `dependent:` handling:**

Batch deletion operations typically use `delete_all`, which bypasses Rails callbacks — `dependent:` options won't fire. But direct deletion via controllers/services uses `destroy`, where `dependent:` options DO matter.

For each FK with `NO ACTION`, check whether the referenced model (the one being pointed TO) declares a `has_many`/`has_one` with an appropriate `dependent:` option for the referencing model. If it doesn't, direct deletion of that model will raise `ActiveRecord::InvalidForeignKey`.

**Step 3 — Search for all deletion paths on the referenced model:**
```bash
# Find all code that destroys/deletes the referenced model
grep -rn "\.destroy\|\.delete\|\.delete_all" app/ --include="*.rb" | grep -i "model_name"
```

**Present findings before implementing.** For each FK with `NO ACTION`, record:

```
| FK constraint             | Batch deletion handled? | Direct deletion handled? | Other deletion paths |
|---------------------------|-------------------------|--------------------------|----------------------|
| table_a.col -> table_b    | [ordering/belongs_to]   | [dependent: option]      | [list paths found]   |
```

A fix that only addresses one deletion path (e.g., fixing batch ordering but not direct deletion) is incomplete.

### External API failures

Honeybadger breadcrumbs often contain the actual API error message that the exception message does not. Look at the `log` breadcrumbs in chronological order for lines like:

```
POST https://api.github.com/repos/.../pulls/.../reviews: 422 - Unprocessable Entity
Error summary: Path could not be resolved, Path could not be resolved...
```

This is more useful than the generic `StandardError: Failed to create pull request review on GitHub.` in the exception message.

### Background job context

For Sidekiq job errors, the Honeybadger context often includes the job arguments. Use these to reconstruct the exact job invocation:

```bash
mise exec -- rails runner "
  # Find the record the job was processing
  record = ModelName.find('id-from-honeybadger-context')
  puts record.inspect

  # Check the state that would have existed when the job ran
  puts record.association.inspect
"
```

## 4. Reproduction

### Database type check

Confirm the database's provenance from the repository setup, import documentation, and the current connection. Do not infer production data from an organization name or a single record. A local production-data copy still requires the relevant authorization. If provenance is unknown, report it as unknown and use disposable local fixtures for reproduction.

### Data verification

```bash
# Check if the local database has the data referenced in the error
mise exec -- rails runner "
  record = ModelName.find_by(field: 'value-from-context')
  puts record.nil? ? 'Record NOT found' : record.inspect
"

# Check for records hidden by default scope
mise exec -- rails runner "
  record = ModelName.unscoped.find_by(field: 'value-from-context')
  puts record.nil? ? 'Record truly does not exist' : 'Hidden by default scope: ' + record.inspect
"
```

### API endpoint reproduction

```bash
# Test an API endpoint with specific parameters from the error context
curl -X POST http://127.0.0.1:3000/api/v1/endpoint \
  -H "Content-Type: application/json" \
  -d '{"param": "value-from-context"}'
```

### Sidekiq job reproduction

```bash
# Invoke a job directly with the arguments from Honeybadger context
mise exec -- rails runner "
  JobClassName.perform_now('arg1-from-context', 'arg2-from-context')
"
```

If the job depends on external services (APIs, webhooks), check if the service can be hit from local or if you need to mock the response.

### Rails console exploration

```bash
# Open an interactive console for deeper investigation
mise exec -- rails console
```

In the console, you can explore associations, scopes, and state interactively. This is useful when the error depends on a chain of associations.

## 5. Fix considerations

- **Prefer explicit exceptions over silent nil propagation.** A nil guard should raise `ActiveRecord::RecordNotFound` (returns 404) rather than letting a `NoMethodError` bubble up (returns 500). The 404 is informative; the 500 is noise.

- **Guard external API calls.** Wrap API calls in begin/rescue with specific error handling. Log the full API error response (status, body, headers) — not just the exception message.

- **Consider Sidekiq retry behavior.** If a job fails and will be retried, will the fix survive retries? If the fix depends on external state (API availability, record existence), the same failure may recur on retry.

- **Check whether the fix needs to span repos.** A backend error might need a fix in the nano engine gem, not the web app. A frontend error caused by a bad API response might need a backend fix.

- **For FK constraint issues, audit both sides of the relationship.** If Model A has a FK column pointing to Model B but the association or dependent handling is missing, check: (1) Does Model B have a `has_many`/`has_one` with the appropriate `dependent:` option? (2) Search for all places that call `destroy`, `delete`, or `delete_all` on Model B across controllers, services, and jobs. (3) Does the FK have `on_delete: :cascade` or `:nullify` at the database level? A missing association affects all deletion paths, not just the one that triggered the error.

- **Default scope fixes.** If a default scope is hiding records that should be found, prefer `unscoped` for the specific query rather than removing the default scope globally.

## 6. Stack-specific traps

### Trap: Gem code under default scope

An association looks correct when you test in console (`Organization.find(id)` works), but returns nil in the actual code path because a default scope filters it. Always check with `Model.unscoped` when debugging nil associations.

### Trap: Breadcrumbs contain the real error

For external API failures, the Honeybadger exception message is often a generic wrapper (e.g., "Failed to create review on GitHub"). The actual API error (422 with specific field errors) is in the `log` breadcrumbs. Always read breadcrumbs chronologically for the full picture.

### Trap: Sidekiq job arguments are stale

The Honeybadger context shows the arguments passed TO the job. But the database state may have changed between when the job was enqueued and when it ran. Check both: the arguments in context AND the current state of the records they reference.

### Trap: Engine code overriding application behavior

Nano engine gems can mount routes, add middleware, and define callbacks that run before application code. If the error comes from application code but the input looks wrong, check if an engine middleware or callback modified the request/data before it reached the application.
