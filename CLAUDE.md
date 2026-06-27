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
