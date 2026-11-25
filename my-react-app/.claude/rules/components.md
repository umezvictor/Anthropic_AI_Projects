---
paths:
  - "src/**/*.jsx"
  - "src/**/*.css"
---

# Component conventions

- Function components and hooks only; `PascalCase.jsx` with a sibling `Component.css`.
- Derive values during render instead of mirroring them in state; never mutate props/state.
- Stable unique `key` on every mapped list.
- Semantic elements, `alt` text on images, keyboard-operable controls.
- Fetch data through `src/api/` functions, not inline in components.
