"""Shared drawing kit for the PixelCursor profile graphics.

Pure standard library, so the daily GitHub Action can run it without installs.
Everything is plain SVG + CSS animation (no scripts): GitHub renders it as an image.

- Text is drawn from outlines in scripts/font.json (JetBrains Mono, OFL), so it looks
  the same on every machine. No web fonts, no fallback fonts.
- The pixel hand comes from scripts/hand.svg, the Clawds from docs/assets/clawd.png.
"""
import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = json.loads((ROOT / 'scripts/font.json').read_text())
SHEET = base64.b64encode((ROOT / 'docs/assets/clawd.png').read_bytes()).decode()
HAND_RAW = (ROOT / 'scripts/hand.svg').read_text()
HAND_W, HAND_H = 476.288, 401.868
HAND_HOT = (0.0313, 0.0741)  # fingertip, as a fraction of width / height

W = 830  # the width GitHub gives a profile README on a desktop screen

# PixelCursor: near-black ground, dots that carry magenta -> violet -> periwinkle
BG, INK, DIM, FAINT, EDGE = '#07070a', '#ececf2', '#9a9ab2', '#5d5d74', '#1e1e2a'
BRAND = [(0, '#f050f0'), (.22, '#b13fe0'), (.45, '#6d28d9'), (.65, '#4f46e5'), (.85, '#8b93ff'), (1, '#b9b9d6')]
# brighter cut of the same ramp, for shapes that must stay readable on black
VIVID = [(0, '#ff66c6'), (.35, '#d2b0ff'), (.7, '#9d9bff'), (1, '#8b93ff')]
# Claude: the orange of the Clawds
ORANGE, HOT, CREAM, GREEN = '#d97757', '#ee9878', '#f5ede0', '#8fd18a'
# the two worlds in one stroke
MIX = [(0, ORANGE), (.34, '#f050f0'), (.68, '#6d28d9'), (1, '#8b93ff')]


def stops(ramp):
    return ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in ramp)


def n(v):
    """Short number for SVG attributes."""
    return f'{v:.2f}'.rstrip('0').rstrip('.')


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.defs, self.css, self.body = [], [], []
        self.glyphs, self.count, self.rules = set(), 0, {}
        self.uses_sheet = self.uses_hand = False
        self.pad = (0, 0)  # transparent margin left / right of the drawing

    def uid(self, prefix='i'):
        self.count += 1
        return f'{prefix}{self.count}'

    def add(self, *parts):
        self.body.extend(parts)

    def rule(self, key, make):
        """One CSS rule per distinct key; returns its class name."""
        if key not in self.rules:
            name = self.uid('c')
            self.rules[key] = name
            self.css.append(make(name))
        return self.rules[key]

    # ---- text ---------------------------------------------------------------
    def text(self, txt, x, y, size, weight='r', fill=INK, anchor='start', ls=0, attrs='', each=None):
        """Outlined text. `each(i, ch)` may return extra attributes per glyph."""
        k = size / FONT['upm']
        adv = FONT['adv'] * k + ls
        width = len(txt) * adv - ls
        x0 = {'start': x, 'middle': x - width / 2, 'end': x - width}[anchor]
        out = []
        for i, ch in enumerate(txt):
            if ch == ' ':
                continue
            self.glyphs.add((weight, ch))
            extra = each(i, ch) if each else ''
            out.append(f'<use href="#{weight}{ord(ch):x}" x="{round(i * adv / k)}"{extra}/>')
        return f'<g transform="translate({n(x0)} {n(y)}) scale({k:.4f})" fill="{fill}"{attrs}>{"".join(out)}</g>'

    def width(self, txt, size, ls=0):
        return len(txt) * (FONT['adv'] * size / FONT['upm'] + ls) - ls

    # ---- timing -------------------------------------------------------------
    def window(self, total, start, length):
        """Attributes that show an element from `start` for `length` seconds in a loop of `total`."""
        pct = length / total * 100
        cls = self.rule(('win', total, round(pct, 3)), lambda c: (
            f'.{c}{{opacity:0;animation:{c} {n(total)}s step-end infinite}}'
            f'@keyframes {c}{{0%{{opacity:1}}{pct:.3f}%{{opacity:0}}100%{{opacity:0}}}}'))
        return f' class="{cls}" style="animation-delay:{n(start)}s"'

    def reveal(self, delay):
        """Attributes for a one-time reveal after `delay` seconds. Visible when animations do not run."""
        cls = self.rule('reveal', lambda c: f'.{c}{{animation:{c} 1ms linear backwards}}@keyframes {c}{{from{{opacity:0}}}}')
        return f' class="{cls}" style="animation-delay:{n(delay)}s"'

    # ---- parts --------------------------------------------------------------
    def gradient(self, ramp, x1, y1, x2, y2):
        gid = self.uid('g')
        self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}">{stops(ramp)}</linearGradient>')
        return gid

    def dots(self, pitch=14, r=1.05, base=.85, lights='', w=None, h=None):
        """The dotted ground: dots carry the brand ramp, `lights` are shapes that light them up."""
        w, h = w or self.w, h or self.h
        pid, mid = self.uid('p'), self.uid('m')
        gid = self.gradient(BRAND, 0, h, w, 0)
        self.defs.append(
            f'<pattern id="{pid}" width="{pitch}" height="{pitch}" patternUnits="userSpaceOnUse"><circle cx="{pitch / 2}" cy="{pitch / 2}" r="{r}" fill="#fff"/></pattern>'
            f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="url(#{pid})"/></mask>')
        return f'<g mask="url(#{mid})"><rect width="{w}" height="{h}" fill="url(#{gid})" opacity="{base}"/>{lights}</g>'

    def glow(self, cx, cy, rx, ry, color, opacity):
        gid = self.uid('g')
        self.defs.append(f'<radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="url(#{gid})"/>'

    def card(self, inner, rx=12, accent=True):
        """Rounded dark card that clips its content; a thin orange-to-violet line on top."""
        cid = self.uid('k')
        self.defs.append(f'<clipPath id="{cid}"><rect width="{self.w}" height="{self.h}" rx="{rx}"/></clipPath>')
        line = ''
        if accent:
            gid = self.gradient(MIX, 0, 0, self.w, 0)
            line = f'<rect width="{self.w}" height="3" fill="url(#{gid})"/>'
        return (f'<g clip-path="url(#{cid})"><rect width="{self.w}" height="{self.h}" fill="{BG}"/>{inner}{line}</g>'
                f'<rect x=".5" y=".5" width="{self.w - 1}" height="{self.h - 1}" rx="{rx - .5}" fill="none" stroke="#fff" stroke-opacity=".09"/>')

    def hand(self, size, attrs=''):
        """The pixel hand, `size` px wide, with its fingertip at the local origin."""
        self.uses_hand = True
        h = size * HAND_H / HAND_W
        return f'<use href="#hand" x="{n(-size * HAND_HOT[0])}" y="{n(-h * HAND_HOT[1])}" width="{n(size)}" height="{n(h)}"{attrs}/>'

    def sprite(self, name, frames, step, scale=2):
        """An animated Clawd from the sheet. frames = [(col, row), ...], `step` seconds each."""
        self.uses_sheet = True
        total = len(frames) * step
        keys = ''.join(f'{i / len(frames) * 100:.3f}%{{transform:translate({-c * 48}px,{-r * 48}px)}}' for i, (c, r) in enumerate(frames))
        cls = self.rule(('sprite', name), lambda c: f'.{c}{{animation:{c} {total:.2f}s step-end infinite}}@keyframes {c}{{{keys}}}')
        return (f'<g transform="scale({scale})"><svg width="48" height="48" viewBox="0 0 48 48" overflow="hidden">'
                f'<use href="#sheet" class="{cls}"/></svg></g>')

    def chrome(self, title, status=None):
        """Window bar: three lights and a path on the left, a status on the right."""
        out = [f'<circle cx="26" cy="26" r="4.5" fill="{ORANGE}"/><circle cx="41" cy="26" r="4.5" fill="#2c2c3a"/><circle cx="56" cy="26" r="4.5" fill="#2c2c3a"/>',
               self.text(title, 74, 30, 11.5, fill=DIM, ls=1)]
        if status:
            x = self.w - 24 - self.width(status, 11, 1.6)
            pulse = self.rule('pulse', lambda c: f'.{c}{{animation:{c} 2s ease-in-out infinite}}@keyframes {c}{{50%{{opacity:.3}}}}')
            out += [f'<circle class="{pulse}" cx="{n(x - 12)}" cy="26" r="3.5" fill="{GREEN}"/>', self.text(status, x, 30, 11, fill=DIM, ls=1.6)]
        return ''.join(out)

    # ---- output -------------------------------------------------------------
    def render(self):
        defs = list(self.defs)
        for weight, ch in sorted(self.glyphs):
            defs.append(f'<path id="{weight}{ord(ch):x}" d="{FONT["glyphs"][weight][ch]}"/>')
        if self.uses_sheet:
            defs.append(f'<image id="sheet" width="480" height="454" style="image-rendering:pixelated" href="data:image/png;base64,{SHEET}"/>')
        if self.uses_hand:
            inner = re.sub(r'^<svg[^>]*>|</svg>\s*$|<title>.*?</title>', '', HAND_RAW)
            inner = re.sub(r'id="([^"]+)"', r'id="H\1"', inner)
            inner = re.sub(r'url\(#([^)]+)\)', r'url(#H\1)', inner)
            box = re.search(r'viewBox="([^"]+)"', HAND_RAW).group(1)
            defs.append(f'<symbol id="hand" viewBox="{box}">{inner}</symbol>')
        left, right = self.pad
        full, body = self.w + left + right, ''.join(self.body)
        if left:
            body = f'<g transform="translate({left} 0)">{body}</g>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{full}" height="{self.h}" viewBox="0 0 {full} {self.h}" role="img" aria-label="{self.label}">'
                f'<style>{"".join(self.css)}</style><defs>{"".join(defs)}</defs>{body}</svg>')

    def save(self, rel):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render())
        print(f'{rel:32} {path.stat().st_size / 1024:6.1f} KB')
