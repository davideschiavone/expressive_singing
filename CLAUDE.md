# Expressive Singing — Project Guide

Static bilingual (EN/FR) website for the Expressive Singing association/company in Geneva.
Plain HTML + CSS + vanilla JS. No build step — files are served as-is.

## Structure
- One `.html` file per page (index, association, company, classes, events, retreats, blog, contact, about, booking).
- `style.css` — all styling, with CSS variables defined in `:root`.
- `main.js` — language toggle, nav, hamburger, fade-in, form handling.
- `images/` — local assets (team photos, community photos, posters, logo).

## Conventions
- **Bilingual text:** every user-facing string carries `data-en` and `data-fr` attributes; `main.js` swaps `textContent` on toggle. Always provide BOTH languages when adding/editing copy.
- **Language button** (`#langBtn`): shows the CURRENT language — `EN` in English, `FR` in French.
- Use the existing CSS variables and component classes (`.content-section`, `.two-col`, `.value-card`, `.btn`, etc.) rather than ad-hoc styles.
- No emoji in the UI (decorative emoji were intentionally removed; functional `✓` markers are allowed).

## Rules
- **Commit after every task.** When a task is finished, run `git add -A && git commit` with a concise, descriptive message before considering it done. One commit per task.
- **Always align repeated UI.** Whenever creating or editing cards/grids or any repeated component (class cards, event cards, membership cards, payment cards, etc.), make them visually consistent: equal card heights, headers/titles starting at the same height (reserve space with `min-height` for 1- vs 2-line titles), fact rows and dividers aligned across cards, and prices/buttons/footers anchored to the same baseline (`margin-top: auto`). Give buttons a fixed `min-height` so 1-line and 2-line labels match (matters for FR, whose labels often wrap). Then **render the page with headless Chromium and visually verify the alignment** before considering the task done.
- **Always provide real EN and FR copy.** Never put the same French (or English) string in both `data-en` and `data-fr`. Proper nouns/event names that don't translate may stay identical, but translate everything else (city names, "shows"/"représentations", etc.).
