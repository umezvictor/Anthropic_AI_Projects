# my-react-app

React 19 + Vite 8 app (plain JavaScript/JSX, ES modules). Linted with oxlint.

## Commands

- `npm run dev` — start the dev server
- `npm run build` — production build
- `npm run lint` — oxlint (config in `.oxlintrc.json`); must pass before finishing any change
- `npm run preview` — serve the production build

## Coding standards

- Function components and hooks only; no class components.
- One component per file, `PascalCase.jsx`, with the component's CSS next to it (`Component.css`). Non-component modules use `camelCase.js`.
- Keep components small and focused; extract shared logic into custom hooks named `useThing`.
- Prefer `const`; never use `var`. Use named exports for everything except a file's single primary component (default export).
- Do not mutate state or props; derive values during render instead of duplicating them in state.
- Every list rendered with `.map` needs a stable, unique `key` (not the array index when items can reorder).
- No `console.log` or commented-out code in committed changes.
- Do not add a dependency when the platform or React already covers the need; justify any new one in the PR.
- Accessibility: use semantic elements, give images `alt` text, and make interactive elements keyboard-operable.
- Fix lint errors rather than disabling rules; any `oxlint-disable` needs a comment explaining why.

## Testing conventions

No test runner is installed yet. When adding the first tests, use Vitest + React Testing Library (it reuses the Vite config) and add a `test` script to `package.json`. Detailed test-writing rules live in `.claude/rules/testing.md` and load when test files are touched.

- New features and bug fixes ship with tests.
- `npm run lint` and `npm test` must both pass before a change is considered done.

## Path-scoped rules

Area-specific conventions live in `.claude/rules/` (`api.md`, `components.md`, `testing.md`). Each has a `paths:` glob in its frontmatter, so it loads only when matching files are touched. Keep universal rules here and area-specific ones there.

## Team consistency

- This file is committed to version control so every team member gets identical instructions. Edit it via pull request.
- Personal preferences go in `CLAUDE.local.md` (gitignored) or `~/.claude/CLAUDE.md`, never here.
