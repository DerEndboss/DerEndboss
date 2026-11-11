# Assets

- **Typeface:** JetBrains Mono (SIL Open Font License 1.1, © The JetBrains Mono Project Authors). The glyph outlines used in the graphics are stored in `scripts/font.json`, so no font file is loaded at view time.
- **Pixel hand:** the PixelCursor mark, own work (`scripts/hand.svg`).
- **Clawd:** the Claude Code mascot belongs to Anthropic. The sprites in `docs/assets/clawd.png` are used as fan art. This profile is not affiliated with or endorsed by Anthropic.

How the graphics are made: `python3 scripts/build_profile.py` draws the hero, the session and the tiles. `scripts/update_stats.py` redraws the contribution calendar once a day through GitHub Actions. Both use `scripts/kit.py` and only the Python standard library.
