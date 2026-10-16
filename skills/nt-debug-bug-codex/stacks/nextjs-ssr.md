# Next.js SSR Investigation Techniques

Techniques for debugging Honeybadger errors from server-side Next.js — middleware, edge runtime, SSR pages, and API routes running on the server.

## 1. Backtrace reading

Next.js server-side code is compiled and minified. Backtraces show file:line:column in the compiled output (e.g., `middleware.js:13:26498`). Source maps are typically NOT available server-side in production.

To find the crash site:

1. **Build locally** to produce the same compiled output:
   ```bash
   yarn build
   ```

2. **Extract code at the crash position** using the line and column numbers from the backtrace:
   ```bash
   # Extract ~200 characters around the crash column
   sed -n '13p' build/server/middleware.js | cut -c26400-26600
   ```

3. **Map back to source** by searching for identifiable strings in the extracted snippet. Look for variable names, string literals, or function names that appear in the source code:
   ```bash
   # Search source files for a distinctive string from the extracted code
   grep -r "identifiable_string" src/ --include="*.ts" --include="*.js" -l
   ```

For API routes and SSR pages, the compiled output is in `build/server/pages/` or `build/server/app/`. For middleware, it is at `build/server/middleware.js`.

## 2. Framework source

Next.js internals are at `node_modules/next/dist/`. Key files to investigate:

- **Image optimizer**: `server/image-optimizer.js` — makes internal HTTP requests through middleware to fetch local images. Uses `fetchInternalImage()` and `createRequestResponseMocks()` to create a mocked request with only url, method, and socket (NO headers).
- **Edge adapter**: `server/web/adapter.js` — adapts requests for edge runtime middleware.
- **Web server**: `server/web-server.js` — handles request routing and middleware invocation.
- **ISR**: `server/incremental-cache*.js` — Incremental Static Regeneration makes background requests to regenerate pages.

Search for internal request creation:
```bash
grep -r "fetchInternalImage\|createRequestResponseMocks\|IncrementalCache" node_modules/next/dist/ --include="*.js" -l
```

## 3. Investigation techniques

### Internal/synthetic requests

Next.js makes internal HTTP requests that go through middleware even though the original URL was excluded by the middleware matcher. The most common:

- **Image optimizer** (`/_next/image`): Excluded by matcher, but the optimizer's internal fetch of the underlying image path (e.g., `/images/foo.png`) goes THROUGH middleware with a mocked request that has NO headers.
- **ISR revalidation**: Background page regeneration makes internal requests.
- **Prefetching**: `/_next/data/` requests for client-side navigation.

### Edge runtime restrictions

Middleware runs in the edge runtime, which has important differences from Node.js:

- **`process.env` is inlined at BUILD time**, not read at runtime. If an environment variable changes after deploy, you must rebuild. Check that the build environment matches production.
- **Limited API surface**: No `fs`, no `child_process`, no native Node.js modules. Some npm packages do not work in edge runtime.
- **Request/Response API**: Uses the Web API (`Request`, `Response`, `Headers`) not Node.js HTTP (`IncomingMessage`, `ServerResponse`).

### Middleware matcher patterns

The middleware `config.matcher` controls which paths hit middleware. Common gotchas:

- A matcher like `/((?!api|_next/static|_next/image|favicon.ico).*)` excludes specific prefixes, but paths that do not start with those prefixes still match — including paths with file extensions like `/images/foo.png`.
- The `\.\w+$` negative lookahead only matches if the dot is the FIRST character after `/`. Paths like `/path/to/file.png` are NOT excluded.

Verify which paths actually hit middleware:
```bash
# Check the matcher in middleware config
grep -A 10 "export const config" src/middleware.ts
```

### Host header dependency

If middleware routes based on the `Host` header:
- HTTP/1.1 requires `Host`. Node.js HTTP server rejects HTTP/1.1 requests without it (returns 400 before reaching middleware).
- HTTP/1.0 does NOT require `Host`. Bots, scanners, and health checks may send HTTP/1.0 requests that bypass the Host requirement and reach middleware with `host = null`.
- Internal framework requests may use mocked request objects with NO headers at all.

Any code path that accesses `host` (e.g., `req.headers.get("host").split(".")`) will crash if host is null.

## 4. Reproduction

**Always use production build mode** for reproducing SSR/middleware bugs:
```bash
yarn build && yarn start
# Server runs at http://localhost:3000
```

Do NOT use `yarn dev` — development mode handles edge runtime, middleware compilation, and static file serving differently.

### Middleware reproduction

```bash
# Test with a valid Host header (normal request)
curl -H "Host: subdomain.example.com" http://127.0.0.1:3000/path

# Test with a custom domain Host
curl -H "Host: customdomain.com" http://127.0.0.1:3000/path

# Test framework internal request (image optimizer)
# This triggers the image optimizer which internally fetches through middleware
curl -H "Host: subdomain.example.com" "http://127.0.0.1:3000/_next/image?url=%2Fimages%2Ftest.png&w=3840&q=75"

# Test HTTP/1.0 without Host header (bot/scanner traffic)
curl --http1.0 -H "Host:" http://127.0.0.1:3000/wp-login.php

# Test with empty Host header (some proxies/load balancers)
curl -H "Host:" http://127.0.0.1:3000/path
```

### SSR page reproduction

```bash
# Request a page that triggers server-side rendering
curl -H "Host: subdomain.example.com" http://127.0.0.1:3000/page-path

# Check the server terminal for errors during rendering
```

### API route reproduction

```bash
# Test API routes with the parameters from Honeybadger context
curl -X POST -H "Host: subdomain.example.com" \
  -H "Content-Type: application/json" \
  -d '{"param": "value-from-context"}' \
  http://127.0.0.1:3000/api/endpoint
```

## 5. Fix considerations

- **Prefer `NextResponse.next()` over returning error responses.** A 400 or 500 response from middleware blocks the request entirely — including legitimate internal framework requests. `NextResponse.next()` lets the request pass through to the next handler safely.

- **Guard all header access with null checks.** Any code that reads `req.headers.get("host")` or similar should handle the case where the header is null. Internal framework requests and HTTP/1.0 clients may not send headers.

- **Middleware runs for more paths than you think.** Verify the matcher regex against the actual URL from the Honeybadger context. The URL that crashed may not be one you expected middleware to process.

- **Edge runtime API limitations.** Ensure your fix uses only Web API-compatible code. Node.js-specific APIs are not available in edge runtime middleware.

- **Rebuild after fixing.** Middleware is compiled at build time. Changes to source code require `yarn build` before they take effect in production mode.

## 6. Stack-specific traps

### Trap: Image optimizer bypasses middleware matcher

The `/_next/image` path is excluded from the middleware matcher, so you might think image requests never hit middleware. But the image optimizer internally fetches the underlying image (e.g., `/images/foo.png`) through middleware using a mocked request with NO headers. The mocked request triggers middleware for a path that would normally be a static file.

### Trap: Stale context from error interceptors

If the application uses an HTTP client (like axios) with an error interceptor that calls `Honeybadger.setContext()`, that context persists across requests within the same server process. When a later middleware crash happens, the stale context from a previous API error gets attached to the new crash report. Do not trust context fields as belonging to the crashing request — investigate when they were set.

### Trap: Edge runtime env vars are build-time constants

`process.env.VARIABLE` in middleware is replaced with the literal value at build time by webpack/turbopack. If the environment variable was not set during `yarn build`, it will be `undefined` in production even if it is set in the runtime environment. Check the build environment, not just the runtime environment.

### Trap: Development mode hides production bugs

`yarn dev` uses a different middleware compilation pipeline, different static file handling, and a different edge runtime polyfill than production. A bug that crashes in production may work fine in development. Always reproduce SSR/middleware bugs with `yarn build && yarn start`.
