# Profile repo

Purpose: the public GitHub profile page (README, animated SVGs, a small browser game in `docs/`), refreshed daily by a GitHub Action.

## How it is built

- `scripts/build_profile.py` draws the SVGs in `assets/` (helpers in `scripts/kit.py`, standard library only).
- `scripts/update_stats.py` refreshes the numbers; `.github/workflows/stats.yml` runs it daily and pushes "Refresh stats".
- `README.md` is hand-written and references the generated SVGs. It is not generated.

## Rules (public repo)

- Everything in English: code, comments, commit messages.
- Nothing private: no personal or machine names, no local or server paths, no references to private repos or tooling.
- No real names, no private email addresses.
- Commits are signed. Do not commit generated caches (`__pycache__/`).
- License is MIT (see `LICENSE`); asset notes live in `ASSETS.md`.
