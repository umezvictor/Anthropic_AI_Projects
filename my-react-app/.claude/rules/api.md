---
paths:
  - "src/api/**/*"
---

# API layer conventions

- All network calls live in `src/api/`; components never call `fetch` directly.
- One module per resource (`users.js`, `orders.js`), exporting named async functions.
- Wrap `fetch` in a shared client that sets headers, parses JSON, and throws an `ApiError` (status + message) on non-2xx responses.
- Read the base URL from `import.meta.env.VITE_API_URL`; never hardcode hosts or secrets.
- Accept an `AbortSignal` option so callers can cancel in-flight requests.
- Return plain data, not `Response` objects.
