# React Frontend Investigation Techniques

Techniques for debugging Honeybadger errors from browser-side JavaScript — React components, CDN-served bundles, client-side validation, and browser-specific issues.

## 1. Backtrace reading

Frontend errors report backtraces with CDN URLs. These map to the repo source:

**Source-mapped backtraces** (Honeybadger shows "We applied a source map to this stack trace"):
- The file paths are already mapped to original source. Read the file and line directly.
- CDN URL path after the domain maps to the repo: `cdn.neetoform.com/javascript/src/utils/index.js:13` → `src/utils/index.js:13`

**Minified backtraces** (no source map applied):
- Check if source maps are deployed to Honeybadger for this project.
- If not, build the project locally and use the bundled output to trace back to source.
- CDN paths containing `/node_modules/` point to vendored dependencies — find the same package version in the local `node_modules/`.

**Mixed backtraces** (some frames mapped, some not):
- Framework/library frames (lodash, React internals, Honeybadger client) may not have source maps. Find the same version locally in `node_modules/`.

Read the Honeybadger client frame (`@honeybadger-io/core/build/src/client.js`) last — it is the error reporting code, not the error source. Start from the frames in application code.

## 2. Framework source

When the backtrace includes frames in vendored dependencies served from CDN:

1. Identify the package and version from `package.json` or `yarn.lock`.
2. Read the local `node_modules/<package>/` equivalent.
3. For core React internals, errors often originate in component lifecycle — check `node_modules/react-dom/` for rendering logic.

Key locations:
- **Honeybadger client**: `node_modules/@honeybadger-io/core/build/src/client.js` — where errors are captured and context is assembled
- **Form libraries** (Formik, React Hook Form): Validation lifecycle, field registration, error array management
- **State management** (Redux, Zustand): State update timing, selector behavior during re-renders

## 3. Investigation techniques

### Browser context analysis

The Honeybadger environment section contains:
- **HTTP_USER_AGENT**: Reveals browser and version. Old browsers (e.g., Chrome 126 when current is 130+) may have different JavaScript runtime behavior. Check if the error is browser-specific.
- **HTTP_REFERER**: Shows where the user navigated from. This can reveal the user flow that leads to the error.

### Error patterns in browser JS

- **`Cannot redefine property`**: A property descriptor conflict — often caused by multiple scripts trying to define the same property on a prototype. Can be browser-version-specific.
- **`Cannot read properties of null/undefined`**: A reference that was expected to exist is missing. Trace the variable back through React component props, state, or context.
- **`Errors array is unavailable`**: Application-level validation error — check the form validation logic and what conditions cause the errors array to not be initialized.

### Breadcrumb analysis

Browser-side Honeybadger breadcrumbs often include:
- **`log` breadcrumbs**: Console warnings from React or third-party libraries. Look for the earliest non-Honeybadger breadcrumb — it often reveals the root trigger.
- **Rapid "Honeybadger Notice" breadcrumbs**: Dozens of notices within milliseconds means a rendering loop is repeatedly triggering the same error. The bug is whatever causes the re-render loop, not the error itself.
- **`navigation` breadcrumbs**: Page transitions that preceded the error.

### React component lifecycle

If the error occurs during rendering:
- Check if a component receives null/undefined props that it does not guard against.
- Check if a component relies on data that is loaded asynchronously and may not be available on first render.
- Check error boundaries — they catch errors but may hide the root cause if they swallow the error silently.

## 4. Reproduction

### Browser reproduction

1. Open the URL from the Honeybadger notice in a browser.
2. Open DevTools (F12) → Console tab to watch for errors.
3. Open DevTools → Network tab to monitor API responses.
4. Reproduce the user flow: if the error context contains form field data, fill out the form matching those fields.

### Browser-specific reproduction

If the error only appears on specific browsers (check User-Agent in Honeybadger environment):
- Use Chrome DevTools → Device Toolbar → User-Agent override to spoof the browser.
- For deeper testing, use BrowserStack or a VM with the target browser version.

### API response reproduction

If the error is caused by an unexpected API response:
1. Check the Network tab for the API call.
2. Replicate the API call with `curl` or in the browser console.
3. If the API returns an error response that the frontend does not handle, the fix may need to go in the frontend error handling OR the backend API.

### Form/validation reproduction

If the Honeybadger context includes form field data (like `validationContext`):
1. Navigate to the form URL from the notice.
2. Fill in the fields matching the context values.
3. Submit and observe the error.
4. Check if specific field values or combinations trigger the validation bug.

## 5. Fix considerations

- **CDN cache invalidation.** Frontend fixes deploy via CDN. After deployment, the old version may be cached. Check if the CDN uses fingerprinted filenames (e.g., `chunk-C4YR2EI5.digested.js`) — if so, new deploys get new filenames and cache is not an issue.

- **Error boundaries.** Adding an error boundary prevents full-page crashes but hides the root cause. Fix the root cause, then add a boundary as defense-in-depth if appropriate.

- **Browser compatibility.** If the error is browser-specific, check if a polyfill or feature detection is needed. Do not assume all users run the latest browser.

- **Null guards on props/state.** If a component receives null data that it should not, the fix might be in the parent component (preventing null from being passed) rather than in the child (guarding against null).

- **Cross-repo fixes.** If the frontend error is caused by a bad API response from the backend, the fix may need to go in the backend repo. Check the API response the frontend receives and whether it matches what the frontend code expects.

## 6. Stack-specific traps

### Trap: Old browser, different runtime

The Honeybadger User-Agent may show an old browser version (e.g., Chrome 126). JavaScript runtime behavior can differ across versions — property definition, prototype handling, and `Proxy` behavior may not match your local testing environment. Do not dismiss the error as "works on my machine."

### Trap: Honeybadger noise in breadcrumbs

Dozens of rapid-fire "Honeybadger Notice" breadcrumbs within milliseconds of each other usually mean a React rendering loop is triggering the same error repeatedly. The real bug is not the error itself but whatever causes the re-render loop. Look for the earliest DISTINCT breadcrumb (like "Unsupported prop change on Elements") for the actual trigger.

### Trap: Source map mismatch

If the deployed code version does not match the source map version, the backtrace line numbers will be wrong. Check the `revision` field in Honeybadger's Application Environment against the current deployed version. If they differ, the source map may be stale.

### Trap: Third-party script interference

Browser extensions, ad blockers, and injected scripts can cause errors that look like application bugs. Check if the error only occurs for a small subset of users and if the backtrace includes unfamiliar file paths.
