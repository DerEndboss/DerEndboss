"""Build assets/hero.svg: the animated profile header with the Clawd crew.

Pure SVG + CSS animation (no scripts), so GitHub renders it crisp at any size.
The Clawd frames come from docs/assets/clawd.png (48 px cells), embedded once.
Run: python3 scripts/build_hero.py
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = (ROOT / 'docs/assets/clawd.png').read_bytes()
W, H = 1120, 460
BG, PANEL, LINE, ORANGE, HOT, CREAM, DIM, SHADOW = (
    '#1F1C1C', '#292323', '#574039', '#D97A58', '#F19B71', '#F5EDE0', '#B59C8D', '#3A2A25')
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

FONT = {
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
    'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    ' ': ['00000'] * 7,
}

# (role, frames as (col, row), seconds per frame, extra css class)
CREW = [
    ('BUILD', [(8, 4), (9, 4), (0, 5), (1, 5)], 0.18, ''),
    ('SHIP', [(3, 8), (4, 8)], 0.35, 'hop'),
    ('COFFEE', [(0, 0), (4, 6), (5, 6), (5, 6), (4, 6), (0, 0)], 0.45, ''),
    ('VIBE', [(3, 5), (4, 5), (5, 5), (6, 5)], 0.22, ''),
    ('HELLO', [(7, 5), (8, 5)], 0.3, ''),
    ('FOCUS', [(0, 0), (6, 4), (6, 4), (6, 4), (1, 0), (0, 0)], 0.4, ''),
    ('REST', [(2, 5)], 1.0, 'breathe'),
]


def wordmark(text, x, y, cell, gap):
    """Pixel letters as rects; returns (rects, width)."""
    rects, cx = [], x
    for ch in text:
        for r, row in enumerate(FONT[ch]):
            for c, bit in enumerate(row):
                if bit == '1':
                    rects.append(f'<rect x="{cx + c * cell}" y="{y + r * cell}" width="{cell}" height="{cell}"/>')
        cx += 5 * cell + gap
    return ''.join(rects), cx - x - gap


def frames_css(name, frames, step):
    total = len(frames) * step
    keys = []
    for i, (c, r) in enumerate(frames):
        keys.append(f'{i / len(frames) * 100:.3f}%{{transform:translate({-c * 48}px,{-r * 48}px)}}')
    return (f'.f-{name}{{animation:k-{name} {total:.2f}s step-end infinite}}'
            f'@keyframes k-{name}{{{"".join(keys)}}}')


def clawd(name, x, y, scale):
    return (f'<g transform="translate({x} {y}) scale({scale})"><svg width="48" height="48" viewBox="0 0 48 48" overflow="hidden">'
            f'<use href="#sheet" class="f-{name}"/></svg></g>')


def build():
    css = [
        f'text{{font-family:{MONO}}}',
        '.hop{animation:hop .7s ease-in-out infinite}@keyframes hop{50%{transform:translateY(-10px)}}',
        '.breathe{animation:breathe 2.4s ease-in-out infinite;transform-origin:center bottom;transform-box:fill-box}'
        '@keyframes breathe{50%{transform:scaleY(.94)}}',
        '.shine{animation:shine 5s ease-in-out infinite}@keyframes shine{0%,55%{transform:translateX(-260px)}100%{transform:translateX(900px)}}',
        '.type{transform-origin:48px 0;animation:type 3.2s steps(56,end) .6s both}@keyframes type{from{transform:scaleX(0)}to{transform:scaleX(1)}}',
        '.dash{animation:dash 1.6s linear infinite}@keyframes dash{to{stroke-dashoffset:-32}}',
        '.rocket{animation:rocket 2.8s ease-in infinite}@keyframes rocket{0%,30%{transform:translateY(0);opacity:1}'
        '85%{transform:translateY(-150px);opacity:1}100%{transform:translateY(-170px);opacity:0}}',
        '.spot{animation:spot 10.5s steps(7,end) infinite}@keyframes spot{from{transform:translateX(0)}to{transform:translateX(1050px)}}',
        '.live{animation:pulse 2s ease-in-out infinite}@keyframes pulse{50%{opacity:.35}}',
    ]
    crew_svg = []
    spacing, x0, ground = 150, 50, 400
    for i, (role, frames, step, extra) in enumerate(CREW):
        name = role.lower()
        css.append(frames_css(name, frames, step))
        x = x0 + i * spacing
        body = clawd(name, x - 12, ground - 41 * 3 - (14 if role == 'REST' else 0), 3)
        crew_svg.append(f'<g class="{extra}">{body}</g>' if extra else body)
        crew_svg.append(f'<text x="{x + 60}" y="{ground + 34}" text-anchor="middle" fill="{DIM}" font-size="15" letter-spacing="3">{role}</text>')
    # the rocket that SHIP keeps launching
    rocket = (f'<g class="rocket"><g transform="translate({x0 + spacing + 108} {ground - 80}) scale(3)">'
              f'<svg width="11" height="25" viewBox="338 384 11 25" overflow="hidden"><use href="#sheet"/></svg></g></g>')

    letters_a, wa = wordmark('DER', 0, 0, 11, 11)
    letters_b, _ = wordmark('ENDBOSS', wa + 33, 0, 11, 11)
    mark = f'<g transform="translate(48 96)">'
    mark += f'<g fill="{SHADOW}" transform="translate(5 5)">{letters_a}{letters_b}</g>'
    mark += f'<g fill="{CREAM}">{letters_a}</g><g fill="{ORANGE}">{letters_b}</g>'
    mark += (f'<clipPath id="wm">{letters_a}{letters_b}</clipPath><g clip-path="url(#wm)">'
             f'<rect class="shine" x="0" y="-20" width="120" height="120" fill="#fff" opacity=".35" transform="skewX(-20)"/></g></g>')

    sheet = base64.b64encode(SHEET).decode()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Der Endboss. Full-stack dev and game maker, shipping with a crew of seven Clawds: build, ship, coffee, vibe, hello, focus, rest.">
<style>{''.join(css)}</style>
<defs><image id="sheet" width="480" height="454" style="image-rendering:pixelated" href="data:image/png;base64,{sheet}"/>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><rect x="11" y="11" width="2" height="2" fill="{LINE}" opacity=".55"/></pattern></defs>
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="10" fill="url(#grid)"/>
<rect x="1.5" y="1.5" width="{W - 3}" height="{H - 3}" rx="9" fill="none" stroke="{LINE}" stroke-width="3"/>
<rect x="1.5" y="1.5" width="{W - 3}" height="4" fill="{ORANGE}"/>
<circle cx="34" cy="38" r="6" fill="{ORANGE}"/><circle cx="54" cy="38" r="6" fill="{LINE}"/><circle cx="74" cy="38" r="6" fill="{LINE}"/>
<text x="100" y="43" fill="{DIM}" font-size="15" letter-spacing="2">~/derendboss</text>
<circle class="live" cx="880" cy="38" r="5" fill="#8FD18A"/><text x="1090" y="43" text-anchor="end" fill="{DIM}" font-size="15" letter-spacing="2">ONLINE · SHIPPING</text>
<text x="48" y="84" fill="{ORANGE}" font-size="18">&gt; whoami</text>
{mark}
<clipPath id="typed"><rect class="type" x="48" y="196" height="40" width="760"/></clipPath>
<text x="48" y="226" fill="{CREAM}" font-size="24" clip-path="url(#typed)">full-stack dev · game maker · ships with a crew of clawds</text>
<text x="48" y="262" fill="{DIM}" font-size="15" letter-spacing="3">REACT · VITE · NODE · PYTHON · GODOT · DOCKER · LINUX</text>
<g class="spot"><rect x="{x0 - 15}" y="{ground - 150}" width="150" height="205" rx="10" fill="{ORANGE}" opacity=".08"/></g>
{rocket}
{''.join(crew_svg)}
<line x1="30" y1="{ground + 6}" x2="{W - 30}" y2="{ground + 6}" stroke="{LINE}" stroke-width="3" stroke-dasharray="16 16" class="dash"/>
</svg>'''
    (ROOT / 'assets/hero.svg').write_text(svg)
    print('assets/hero.svg', len(svg) // 1024, 'KB')


if __name__ == '__main__':
    build()
