# ✿ Pastel Tech profile — how it works & how to update it

## Structure

```
sofiaas16/                      ← your profile repo (sofiaas16/sofiaas16)
├── README.md                   ← the profile itself
├── assets/                     ← 30 SVGs (light + dark), all generated
├── scripts/
│   ├── build_assets.py         ← THE source of every SVG (palette, texts, projects)
│   ├── sprite.py               ← pixel-art Sara (light-brown hair) at her laptop
│   ├── icons.json              ← official tech logos (Simple Icons / Font Awesome paths)
│   └── coffeeland-preview.jpg  ← CoffeeLand screenshot used in its card
├── profile/                    ← stats cards, written by the stats workflow
└── .github/workflows/
    └── stats.yml               ← stats + top languages → profile/*.svg (daily)
```

## Publish (one time)

### Profile repo `sofiaas16/sofiaas16`
1. **Settings → Actions → General → Workflow permissions → "Read and write permissions"** → Save.
2. **Actions** tab → run **📊 Pastel stats** once ("Run workflow").
   Until it runs, the stats images look broken — that's expected.
3. Section 05 "Take a little break!" only has its header for now — add your game below it in `README.md`.

## Everyday updates

| I want to… | Do this |
|---|---|
| Change colours, texts, typing phrases, tech, projects | Edit `scripts/build_assets.py` → `python3 scripts/build_assets.py` → commit `assets/` |
| Add a technology | Add it to `STACK` (icon names are in `icons.json`; add new ones from Simple Icons) |
| Add a project | Add an entry to `PROJECTS`, rebuild, then copy a project block in `README.md` |
| Refresh stats now | Actions → run the workflow manually |
| Tweak stats colours | Edit `LIGHT` / `DARK` in `.github/workflows/stats.yml` |

Python 3 standard library only — nothing to install.

## Notes
- All animations are CSS inside SVG (works in GitHub's `<img>`); no JavaScript or iframes in the README.
- Light/dark variants switch with `<picture>` + `prefers-color-scheme`, and every image has its own
  solid background, so text never loses contrast.
- Workflows use only `GITHUB_TOKEN` with minimal permissions — no personal tokens or secrets.
- The stats are generated inside your repo instead of the public github-readme-stats server,
  which is often rate-limited.
