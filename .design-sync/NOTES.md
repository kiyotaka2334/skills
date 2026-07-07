# design-sync notes — @courtandclover/ui

- This repo is NOT a pre-existing design-system repo: the package at `cc-ui/` was authored during the first sync (user-approved) from the Court & Clover static site's CSS design system (`courtandclover/css/main.css` is the source of truth for the look).
- The DS package lives at `cc-ui/`; build with `npm --prefix cc-ui run build` (tsc → `cc-ui/dist/` + copies `styles.css`). Converter entry: `cc-ui/dist/index.js`, node_modules: `cc-ui/node_modules`.
- No provider/context needed — the system is plain CSS classes (`cc-*` prefix) + tokens (`--cc-*`).
- Fonts: Playfair Display + Inter variable TTFs committed at `cc-ui/fonts/` (SIL OFL, from google/fonts) with `fonts/fonts.css` wired via `extraFonts`.
- DesignSync tool is NOT authorizable from this remote session (`/design-login` needs an interactive terminal). Upload requires the user to act (Claude Design "Send to Claude Code Web", or run the sync from an interactive session).

## Re-sync risks

- The site CSS (`courtandclover/css/main.css`) and `cc-ui/src/styles.css` are parallel implementations — a change to the site's design tokens does not automatically flow into the package; port changes manually.
- Playwright/chromium in this environment comes from the preinstalled global (`/opt/node22/lib/node_modules/playwright`, browsers at `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`) — do not `playwright install`.
