---
paths:
  - "**/*.test.*"
  - "**/*.spec.*"
---

# Testing conventions

- Use Vitest + React Testing Library; co-locate as `Component.test.jsx`.
- Query by role/label/text (`getByRole` first); avoid test IDs and implementation details.
- One behaviour per `it`, named as a sentence; arrange / act / assert.
- No real network or timers: mock `src/api/*` modules and use fake timers.
- Tests must be independent and deterministic; reset mocks in `afterEach`.
- A bug fix starts with a failing test that reproduces it.
