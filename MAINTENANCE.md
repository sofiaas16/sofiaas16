# ✿ Pastel Tech profile — how it works & how to update it

## Structure

```
sofiaas16/                      ← your profile repo (sofiaas16/sofiaas16)
├── README.md                   ← the profile itself
├── assets/                     ← 34 SVGs (light + dark), all generated
├── scripts/
│   ├── build_assets.py         ← THE source of every SVG (palette, texts, projects)
│   ├── sprite.py               ← pixel-art Sara (light-brown hair) at her laptop
│   ├── icons.json              ← official tech logos (Simple Icons / Font Awesome paths)
│   └── coffeeland-preview.jpg  ← CoffeeLand screenshot used in its card
├── profile/                    ← stats cards, written by the stats workflow
└── .github/workflows/
    ├── snake.yml               ← pastel contribution snake → `output` branch (daily)
    └── stats.yml               ← stats + top languages → profile/*.svg (daily)

pastel-snake/                   ← NEW separate repo (sofiaas16/pastel-snake)
├── index.html · style.css · game.js · main.js · favicon.svg
├── tests/game.test.js          ← `node tests/game.test.js`
└── .github/workflows/pages.yml ← tests + deploys to GitHub Pages
```

## Publish (one time)

### 1. Profile repo `sofiaas16/sofiaas16`
1. Replace `README.md` and add `assets/`, `scripts/`, `.github/`, `MAINTENANCE.md`.
   (`me.gif` is no longer used — 7.5 MB; delete it or keep it, your call.)
2. **Settings → Actions → General → Workflow permissions → "Read and write permissions"** → Save.
3. **Actions** tab → run **🐍 Pastel snake** and **📊 Pastel stats** once ("Run workflow").
   Until they run, the snake and stats images will look broken — that's expected.

### 2. Game repo `sofiaas16/pastel-snake`
1. Create a **public** repo named exactly `pastel-snake` and upload the `pastel-snake/` contents
   (including the hidden `.github` folder).
2. **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Push to `main` (or re-run the workflow). It goes live at
   **https://sofiaas16.github.io/pastel-snake/** — that's the link already in the README.

## Everyday updates

| I want to… | Do this |
|---|---|
| Change colours, texts, typing phrases, tech, projects | Edit `scripts/build_assets.py` → `python3 scripts/build_assets.py` → commit `assets/` |
| Add a technology | Add it to `STACK` (icon names are in `icons.json`; add new ones from Simple Icons) |
| Add a project | Add an entry to `PROJECTS`, rebuild, then copy a project block in `README.md` |
| Refresh stats / snake now | Actions → run the workflow manually |
| Tweak stats colours | Edit `LIGHT` / `DARK` in `.github/workflows/stats.yml` |
| Tweak snake colours | Edit `color_snake` / `color_dots` in `.github/workflows/snake.yml` |

Python 3 standard library only — nothing to install.

## Notes
- All animations are CSS inside SVG (works in GitHub's `<img>`); no JavaScript or iframes in the README.
- Light/dark variants switch with `<picture>` + `prefers-color-scheme`, and every image has its own
  solid background, so text never loses contrast.
- Workflows use only `GITHUB_TOKEN` with minimal permissions — no personal tokens or secrets.
- The stats are generated inside your repo instead of the public github-readme-stats server,
  which is often rate-limited.
