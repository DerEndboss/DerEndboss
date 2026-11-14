"""Build the static profile graphics: hero, session and the six app tiles.

Run: python3 scripts/build_profile.py
The contribution graph (assets/grind.svg) is data and comes from update_stats.py.
"""
import math

from kit import (BG, BRAND, CREAM, DIM, FAINT, GREEN, HOT, INK, MIX, ORANGE, VIVID, W, Svg, n, stops)

# (role, frames as (col, row) on the Clawd sheet, seconds per frame, extra motion)
CREW = [
    ('BUILD', [(8, 4), (9, 4), (0, 5), (1, 5)], 0.18, ''),
    ('SHIP', [(3, 8), (4, 8)], 0.35, 'bounce'),
    ('COFFEE', [(0, 0), (4, 6), (5, 6), (5, 6), (4, 6), (0, 0)], 0.45, ''),
    ('VIBE', [(3, 5), (4, 5), (5, 5), (6, 5)], 0.22, ''),
    ('HELLO', [(7, 5), (8, 5)], 0.3, ''),
    ('FOCUS', [(0, 0), (6, 4), (6, 4), (6, 4), (1, 0), (0, 0)], 0.4, ''),
    ('REST', [(2, 5)], 1.0, 'breathe'),
]
IDLE = [(0, 0)] * 9 + [(1, 0)]
MOTION = {
    'bounce': '.bounce{animation:bounce .7s ease-in-out infinite}@keyframes bounce{50%{transform:translateY(-7px)}}',
    'breathe': '.breathe{animation:breathe 2.4s ease-in-out infinite}@keyframes breathe{50%{transform:scaleY(.93)}}',
}


def lerp(ramp, t):
    """Colour at position t (0..1) of a ramp of (offset, '#rrggbb')."""
    for (o1, c1), (o2, c2) in zip(ramp, ramp[1:]):
        if t <= o2:
            f = (t - o1) / (o2 - o1)
            a, b = (int(c1[i:i + 2], 16) for i in (1, 3, 5)), (int(c2[i:i + 2], 16) for i in (1, 3, 5))
            return '#' + ''.join(f'{round(x + (y - x) * f):02x}' for x, y in zip(a, b))
    return ramp[-1][1]


def keyframes(name, points, total, prop=lambda v: v):
    """@keyframes from [(seconds, value), ...]."""
    return f'@keyframes {name}{{' + ''.join(f'{t / total * 100:.3f}%{{{prop(v)}}}' for t, v in points) + '}'


# ---------------------------------------------------------------- hero ------
def hero():
    s = Svg(W, 400, 'PixelCursor. Apps, games and tools, shipped with a crew of seven Clawds: build, ship, coffee, vibe, hello, focus, rest. The pixel hand clicks through the crew.')
    ground, loop, beat = 346, 17.5, 2.5
    centers = [79 + i * 112 for i in range(7)]
    tips = [(cx + 22, ground + 21) for cx in centers]  # where the fingertip presses each role

    # ground: dots that light up under a slow drift and under every click
    s.defs.append('<radialGradient id="ring"><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#ffe3f6" stop-opacity="1"/>'
                  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
                  '<radialGradient id="soft"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')
    s.css.append('.drift{animation:drift 24s ease-in-out infinite alternate}@keyframes drift{from{transform:translate(-80px,330px)}to{transform:translate(900px,60px)}}'
                 f'.rip{{opacity:0;animation:rip {loop}s ease-out infinite}}@keyframes rip{{0%{{opacity:1;transform:scale(.06)}}8%{{opacity:0;transform:scale(1)}}100%{{opacity:0;transform:scale(1)}}}}')
    lights = '<g class="drift"><circle r="210" fill="url(#soft)"/></g>'
    for i, (x, y) in enumerate(tips):
        lights += f'<g transform="translate({x} {y})"><circle class="rip" style="animation-delay:{n(i * beat + 1)}s" r="190" fill="url(#ring)"/></g>'
    back = (s.glow(0, 400, 430, 250, '#f050f0', .2) + s.glow(W, 0, 430, 250, '#6e6ec8', .2) + s.glow(W / 2, 410, 430, 110, ORANGE, .13)
            + s.dots(r=1.2, base=1, lights=lights) + s.glow(300, 140, 400, 120, BG, .94))

    # the lockup: hand + wordmark, typed once, then a slow shine
    size, x0, base = 70, 142, 143
    adv = 600 * size / 1000 - 1.5
    s.defs.append('<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="900" y2="-260"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                  '<stop offset=".5" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
                  '<animateTransform attributeName="gradientTransform" type="translate" values="-1600 0;-1600 0;8200 0" keyTimes="0;.6;1" dur="7s" repeatCount="indefinite"/></linearGradient>')
    word = 'PixelCursor'
    s.css.append(f'.caret{{animation:caret {n(len(word) * .07)}s steps({len(word)},end) .4s backwards}}@keyframes caret{{from{{transform:translateX({n(-len(word) * adv)}px)}}}}'
                 '.blink{animation:blink 1.1s step-end infinite}@keyframes blink{50%{opacity:0}}')
    mark = (f'<g transform="translate(36 80)">{s.hand(90)}</g>'
            + s.text(word, x0, base, size, 'x', ls=-1.5, each=lambda i, ch: s.reveal(.4 + i * .07))
            + s.text(word, x0, base, size, 'x', fill='url(#shine)', ls=-1.5)
            + f'<g class="caret"><rect class="blink" x="{n(x0 + len(word) * adv + 6)}" y="{base - 52}" width="15" height="53" fill="{ORANGE}"/></g>')
    tag = 'apps · games · tools · shipped with a crew of clawds'
    words = (s.text('>', 36, 64, 14, 'b', fill=ORANGE) + s.text('whoami', 54, 64, 14, fill=ORANGE)
             + s.text(tag, 36, 192, 16.5, fill=CREAM, each=lambda i, ch: s.reveal(1.5 + i * .04))
             + s.text('REACT · VITE · NODE · PYTHON · GODOT · DOCKER · LINUX', 36, 218, 10.5, 'b', fill=DIM, ls=2.4))

    # the crew: the hand presses a role, the role lights up, its Clawd hops
    s.css.append(MOTION['bounce'] + MOTION['breathe']
                 + f'.hop{{animation:hop {loop}s ease-out infinite}}@keyframes hop{{0%{{transform:none}}1.3%{{transform:translateY(-10px)}}2.8%{{transform:none}}100%{{transform:none}}}}'
                 '.dash{animation:dash 1.6s linear infinite}@keyframes dash{to{stroke-dashoffset:-20}}'
                 '.rocket{animation:rocket 2.8s ease-in infinite}@keyframes rocket{0%,30%{transform:none;opacity:1}85%{transform:translateY(-62px);opacity:1}100%{transform:translateY(-74px);opacity:0}}')
    crew = [f'<line class="dash" x1="24" y1="{ground + 3}" x2="{W - 24}" y2="{ground + 3}" stroke="#2b2b3b" stroke-width="2" stroke-dasharray="10 10"/>']
    for i, (role, frames, step, extra) in enumerate(CREW):
        cx, at = centers[i], i * beat + 1
        body = f'<g transform="translate(-48 -82)">{s.sprite(role.lower(), frames, step)}</g>'
        if extra:
            body = f'<g class="{extra}">{body}</g>'
        body = f'<g transform="translate({cx} {ground})">{body}</g>'
        if role == 'SHIP':
            s.uses_sheet = True
            crew.append(f'<g class="rocket"><g transform="translate({cx + 26} {ground - 54}) scale(2)"><svg width="11" height="25" viewBox="338 384 11 25" overflow="hidden"><use href="#sheet"/></svg></g></g>')
        crew.append(f'<g class="hop" style="animation-delay:{n(at)}s">{body}</g>')
        win = s.window(loop, at, beat)
        crew.append(s.text(role, cx, ground + 27, 10.5, 'b', fill=DIM, anchor='middle', ls=2.2)
                    + f'<g{win}><rect x="{cx - 41}" y="{ground + 11}" width="82" height="24" rx="12" fill="{BG}"/>'
                    f'<rect x="{cx - 40.5}" y="{ground + 11.5}" width="81" height="23" rx="11.5" fill="{ORANGE}" fill-opacity=".16" stroke="{ORANGE}" stroke-opacity=".75"/>'
                    + s.text(role, cx, ground + 27, 10.5, 'b', fill=HOT, anchor='middle', ls=2.2) + '</g>')

    # the cursor
    path = [(0, tips[-1])]
    for i, tip in enumerate(tips):
        path += [(i * beat + .9, tip), ((i + 1) * beat, tip)]
    s.css.append(f'.cur{{animation:cur {loop}s ease-in-out infinite}}' + keyframes('cur', path, loop, lambda p: f'transform:translate({p[0]}px,{p[1]}px)')
                 + f'.press{{animation:press {beat}s ease-out infinite}}@keyframes press{{0%,36%{{transform:none}}40%{{transform:scale(.8)}}48%,100%{{transform:none}}}}')
    cursor = f'<g class="cur"><g class="press">{s.hand(36)}</g></g>'

    s.add(s.card(back + s.chrome('~/pixelcursor', 'ONLINE · SHIPPING') + words + mark + ''.join(crew) + cursor))
    s.save('assets/hero.svg')


# ------------------------------------------------------------- session ------
SCENES = [
    ('a chess app. stockfish in the browser, no account.', 'analysis · game review · puzzles · play', 'relentchess.pixel-cursor.com'),
    ('a hydration tracker with water that really moves.', 'quick add · goal calculator · streaks · reminders', 'drinkbro.pixel-cursor.com'),
    ('a game where every level is a real dark pattern.', '20 forms · 20 dark patterns · say no', 'iagree.pixel-cursor.com'),
]


def session():
    s = Svg(W, 270, 'A Claude session, looping through three apps that were built this way: a prompt, a plan, the build, the checks, and a live address. '
                    'RelentChess, DrinkBro and I Have Read and Agree.')
    each, loop = 10, 10 * len(SCENES)
    work, live = 2.9, 8.4  # seconds into a scene: Claude starts working / the app is live
    stay = 14  # how long a line stays on; its scene fades out before that
    s.css.append(f'.scene{{opacity:0;animation:scene {loop}s linear infinite}}@keyframes scene{{0%{{opacity:0}}.6%{{opacity:1}}{(each - .5) / loop * 100:.2f}%{{opacity:1}}{(each - .1) / loop * 100:.2f}%{{opacity:0}}100%{{opacity:0}}}}'
                 '.sp{opacity:0;animation:sp .56s step-end infinite}@keyframes sp{0%{opacity:1}25%{opacity:0}100%{opacity:0}}' + MOTION['bounce'])
    bar = s.gradient(VIVID, 122, 0, 362, 0)
    star = ''.join(f'<g class="sp" style="animation-delay:{n(i * .14)}s" stroke="{ORANGE}" stroke-linecap="round" fill="none">{shape}</g>' for i, shape in enumerate([
        f'<circle r="1.6" fill="{ORANGE}" stroke="none"/>',
        '<path stroke-width="2" d="M-4 0H4M0-4V4"/>',
        '<path stroke-width="2" d="M-6 0H6M-3-5.2L3 5.2M3-5.2L-3 5.2"/>',
        '<path stroke-width="2.2" d="M-7 0H7M0-7V7M-5-5L5 5M5-5L-5 5"/>']))
    out = []
    for k, (prompt, plan, host) in enumerate(SCENES):
        t0 = k * each
        on = lambda t, length=stay: s.window(loop, t0 + t, length)
        adv = 600 * 14 / 1000
        car = s.uid('c')
        typed = .4 + len(prompt) * .042
        s.css.append(f'.{car}{{animation:{car} {loop}s linear infinite;animation-delay:{t0}s}}@keyframes {car}{{0%{{transform:none}}{.4 / loop * 100:.3f}%{{transform:none;animation-timing-function:steps({len(prompt)},end)}}'
                     f'{typed / loop * 100:.3f}%{{transform:translateX({n(len(prompt) * adv)}px)}}100%{{transform:translateX({n(len(prompt) * adv)}px)}}}}')
        rows = [s.text('>', 36, 76, 14, 'b', fill=ORANGE),
                s.text(prompt, 58, 76, 14, fill=CREAM, each=lambda i, ch: on(.4 + i * .042)),
                f'<g{on(0, work)}><rect class="{car}" x="59" y="63" width="8" height="16" fill="{ORANGE}"/></g>']

        def line(y, t, verb, detail):
            return (f'<g{on(t)}><circle cx="41" cy="{y - 4.5}" r="3.2" fill="#8b93ff"/>' + s.text(verb, 56, y, 13, 'b', fill=INK) + '</g>' + detail)

        cells = ''.join(f'<rect x="{122 + j * 12}" y="131" width="9" height="9" rx="1.5" fill="#23232f"/>' for j in range(20))
        fill = ''.join(f'<rect x="{122 + j * 12}" y="131" width="9" height="9" rx="1.5" fill="url(#{bar})"{on(4.5 + j * .09)}/>' for j in range(20))
        checks = ''.join(f'<g{on(6.75 + j * .3)}>' + s.text(word, 122 + j * 82, 166, 13, fill=DIM) + s.text('✓', 122 + j * 82 + len(word) * 7.8 + 6, 166, 13, 'b', fill=GREEN) + '</g>'
                         for j, word in enumerate(['lint', 'tests', 'build']))
        url_w = s.width(host, 13)
        rows += [line(114, 3.5, 'Plan', f'<g{on(3.6)}>' + s.text(plan, 122, 114, 13, fill=DIM) + '</g>'),
                 line(140, 4.3, 'Build', f'<g{on(4.3)}>{cells}</g>{fill}'),
                 line(166, 6.6, 'Check', checks),
                 line(192, 7.8, 'Deploy', f'<g{on(7.9)}>' + s.text(host, 122, 192, 13, 'b', fill=CREAM) + '</g>'
                      + f'<g{on(live)}><circle cx="{n(122 + url_w + 16)}" cy="187.5" r="3.5" fill="{GREEN}"/>' + s.text('live', 122 + url_w + 26, 192, 13, 'b', fill=GREEN) + '</g>'),
                 f'<g{on(work, live - work)}><g transform="translate(42 229)">{star}</g>' + s.text('Shipping…', 56, 234, 13, fill=ORANGE) + '</g>',
                 f'<g{on(live)}>' + s.text('✓', 36, 234, 13, 'b', fill=GREEN) + s.text('shipped', 56, 234, 13, fill=GREEN) + '</g>']
        out.append(f'<g class="scene" style="animation-delay:{t0}s">{"".join(rows)}</g>')

        # the Clawd at the desk: waits for the prompt, types while Claude works, cheers when it is live
        cx, top = 606, 54
        states = [(0, work, s.sprite('idle', IDLE, .28, 4), ''), (work, live - work, s.sprite('build', CREW[0][1], .18, 4), ''),
                  (live, each - live, s.sprite('ship', CREW[1][1], .35, 4), 'bounce')]
        for start, length, body, extra in states:
            body = f'<g transform="translate({cx} {top})">{body}</g>'
            out.append(f'<g{s.window(loop, t0 + start, length)}>' + (f'<g class="{extra}">{body}</g>' if extra else body) + '</g>')

    back = (s.glow(0, 270, 380, 200, '#f050f0', .14) + s.glow(W, 0, 380, 200, '#6e6ec8', .2) + s.glow(702, 250, 200, 80, ORANGE, .24)
            + s.dots(base=.7) + s.glow(300, 150, 450, 170, BG, .95))
    floor = f'<line x1="596" y1="222" x2="806" y2="222" stroke="#2b2b3b" stroke-width="2" stroke-dasharray="10 10"/>'
    s.add(s.card(back + s.chrome('~/pixelcursor · claude') + floor + ''.join(out)))
    s.save('assets/session.svg')


# --------------------------------------------------------------- tiles ------
MX, MY = 340, 75  # centre of the motif area on a tile


def m_sort(s):
    """Seven bars bubble-sort themselves into the brand ramp, then shuffle back."""
    vals, bw, pitch, base = [4, 2, 6, 1, 7, 3, 5], 10, 15, 118
    x0 = MX - (6 * pitch + bw) / 2
    slot_of, arr, ids = {i: i for i in range(7)}, vals[:], list(range(7))
    track, t = {i: [(0, i)] for i in range(7)}, .7
    for a in range(6):
        for b in range(6 - a):
            if arr[b] > arr[b + 1]:
                arr[b], arr[b + 1] = arr[b + 1], arr[b]
                ids[b], ids[b + 1] = ids[b + 1], ids[b]
                for bar, new in ((ids[b], b), (ids[b + 1], b + 1)):
                    track[bar] += [(t, slot_of[bar]), (t + .3, new)]
                    slot_of[bar] = new
                t += .4
    total = t + 2.6
    out = []
    for i, v in enumerate(vals):
        name = s.uid('b')
        pts = track[i] + [(total - 1, slot_of[i]), (total - .35, i), (total, i)]
        s.css.append(f'.{name}{{animation:{name} {n(total)}s ease-in-out infinite}}' + keyframes(name, pts, total, lambda sl: f'transform:translateX({sl * pitch}px)'))
        h = 12 + v * 11
        out.append(f'<rect class="{name}" x="{n(x0)}" y="{base - h}" width="{bw}" height="{h}" rx="2" fill="{lerp(VIVID, (v - 1) / 6)}"/>')
    return ''.join(out) + f'<rect x="{n(x0 - 4)}" y="{base + 4}" width="{6 * pitch + bw + 8}" height="2" rx="1" fill="#2b2b3b"/>'


KNIGHT = ['...##....', '..####...', '.######..', '###.####.', '########.', '.##.####.', '...#####.', '..#####..', '..#####..', '.#######.', '.#######.']


def m_chess(s):
    """A pixel knight tours a small board while the evaluation bar follows."""
    cell, x0, y0 = 22, 300, 31
    board = ''.join(f'<rect x="{x0 + c * cell}" y="{y0 + r * cell}" width="{cell}" height="{cell}" fill="#fff" fill-opacity="{.13 if (c + r) % 2 == 0 else .045}"/>'
                    for r in range(4) for c in range(4))
    px = ''.join(f'M{c} {r}h1v1h-1z' for r, row in enumerate(KNIGHT) for c, bit in enumerate(row) if bit == '#')
    stops_, beat, total = [(0, 3), (1, 1), (3, 0), (2, 2)], 1.5, 6
    pts, bar = [], []
    for i, (c, r) in enumerate(stops_):
        pts += [(i * beat, (c, r)), (i * beat + 1, (c, r))]
        bar += [(i * beat, [.5, .6, .42, .68][i]), (i * beat + 1, [.5, .6, .42, .68][i])]
    pts.append((total, stops_[0]))
    bar.append((total, .5))
    s.css.append(f'.kn{{animation:kn {total}s ease-in-out infinite}}' + keyframes('kn', pts, total, lambda p: f'transform:translate({p[0] * cell}px,{p[1] * cell}px)')
                 + f'.ev{{animation:ev {total}s ease-in-out infinite}}' + keyframes('ev', bar, total, lambda f: f'transform:scaleY({f})'))
    g = s.gradient(VIVID, 0, y0 + 88, 0, y0)
    return (f'<rect x="{x0}" y="{y0}" width="88" height="88" rx="3" fill="#101018"/>{board}'
            f'<rect x="{x0 - 12}" y="{y0}" width="5" height="88" rx="2.5" fill="#23232f"/>'
            f'<g transform="translate({x0 - 12} {y0 + 88})"><rect class="ev" y="-88" width="5" height="88" rx="2.5" fill="url(#{g})" transform="translate(0 0)"/></g>'
            f'<g transform="translate({x0 + 3.8} {y0 + 2.2})"><g class="kn"><path transform="scale(1.6)" d="{px}" fill="{INK}"/></g></g>')


def m_water(s):
    """A round glass: two waves run against each other while the level breathes."""
    r, period = 44, 56
    wave = 'M-140 0' + ''.join(f'L{x} {n(4 * math.sin(x / period * 2 * math.pi))}' for x in range(-136, 201, 4)) + 'V120H-140Z'
    cid = s.uid('k')
    g = s.gradient([(0, '#9d9bff'), (1, '#4f46e5')], 0, -20, 0, 60)
    s.defs.append(f'<clipPath id="{cid}"><circle cx="{MX}" cy="{MY}" r="{r}"/></clipPath>')
    s.css.append(f'.w1{{animation:w1 2.6s linear infinite}}@keyframes w1{{to{{transform:translateX(-{period}px)}}}}'
                 f'.w2{{animation:w2 3.8s linear infinite}}@keyframes w2{{from{{transform:translateX(-{period}px)}}}}'
                 '.lvl{animation:lvl 9s ease-in-out infinite alternate}@keyframes lvl{from{transform:translateY(26px)}to{transform:translateY(-20px)}}')
    return (f'<circle cx="{MX}" cy="{MY}" r="{r}" fill="#101018"/>'
            f'<g clip-path="url(#{cid})"><g transform="translate({MX} {MY})"><g class="lvl"><path class="w2" d="{wave}" fill="#8b93ff" opacity=".4" transform="translate(0 0)"/>'
            f'<g transform="translate(14 3)"><path class="w1" d="{wave}" fill="url(#{g})"/></g></g></g></g>'
            f'<circle cx="{MX}" cy="{MY}" r="{r}" fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1.5"/>'
            f'<path d="M{MX - 30} {MY - 18}A35 35 0 0 1 {MX - 12} {MY - 33}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="2" stroke-linecap="round"/>')


def m_agree(s):
    """The hand unticks the consent box. The box ticks itself again."""
    total, bx, by = 6.5, 282, 34
    g = s.gradient(VIVID, bx, 0, bx + 104, 0)
    pct = lambda t: f'{t / total * 100:.2f}%'
    s.css.append(f'.tick{{animation:tick {total}s step-end infinite}}@keyframes tick{{0%{{opacity:1}}{pct(1.7)}{{opacity:0}}{pct(3.5)}{{opacity:1}}}}'
                 f'.wig{{animation:wig {total}s ease-in-out infinite}}@keyframes wig{{0%,{pct(3.45)}{{transform:none}}{pct(3.6)}{{transform:rotate(-12deg) scale(1.15)}}{pct(3.75)}{{transform:rotate(9deg) scale(1.15)}}'
                 f'{pct(3.9)}{{transform:rotate(-5deg)}}{pct(4.05)},100%{{transform:none}}}}'
                 f'.ac{{animation:ac {total}s ease-in-out infinite}}' + keyframes('ac', [(0, (140, 126)), (.5, (140, 126)), (1.5, (12, 12)), (2, (12, 12)), (2.9, (140, 126)), (total, (140, 126))], total,
                                                                                lambda p: f'transform:translate({p[0]}px,{p[1]}px)')
                 + f'.ap{{animation:ap {total}s ease-out infinite}}@keyframes ap{{0%,{pct(1.6)}{{transform:none}}{pct(1.7)}{{transform:scale(.8)}}{pct(1.85)},100%{{transform:none}}}}')
    return (f'<g transform="translate({bx + 10} {by + 10})"><g class="wig"><rect x="-10" y="-10" width="20" height="20" rx="5" fill="#101018" stroke="#fff" stroke-opacity=".3" stroke-width="1.5"/>'
            f'<path class="tick" d="M-5 0l3.5 3.8L5.5-4.2" fill="none" stroke="#ff66c6" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></g></g>'
            + s.text('Share my data', bx + 28, by + 9, 10, 'b', fill=INK) + s.text('with 847 partners', bx + 28, by + 22, 8.5, fill=DIM)
            + f'<rect x="{bx}" y="{by + 40}" width="104" height="27" rx="13.5" fill="url(#{g})"/>' + s.text('ACCEPT ALL', bx + 52, by + 57.5, 10, 'x', fill='#14091f', anchor='middle', ls=1)
            + s.text('reject', bx + 52, by + 84, 7.5, fill=FAINT, anchor='middle')
            + f'<g transform="translate({bx} {by})"><g class="ac"><g class="ap">{s.hand(24)}</g></g></g>')


def m_seats(s):
    """Guests take their seats around a table, one by one."""
    total = 7
    s.css.append(f'.seat{{transform:scale(0);animation:seat {total}s ease-out infinite}}@keyframes seat{{0%{{transform:scale(0)}}3.5%{{transform:scale(1.25)}}6%{{transform:scale(1)}}80%{{transform:scale(1)}}85%{{transform:scale(0)}}100%{{transform:scale(0)}}}}')
    out = [f'<circle cx="{MX}" cy="{MY}" r="25" fill="#14141d" stroke="#fff" stroke-opacity=".2" stroke-width="1.5"/>', s.text('T1', MX, MY + 4, 10.5, 'b', fill=DIM, anchor='middle')]
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        out.append(f'<g transform="translate({n(MX + 41 * math.cos(a))} {n(MY + 41 * math.sin(a))})"><circle r="7.5" fill="none" stroke="#fff" stroke-opacity=".14" stroke-dasharray="2.5 2.5"/>'
                   f'<circle class="seat" style="animation-delay:{n(.4 + i * .38)}s" r="7.5" fill="{lerp(VIVID, i / 7)}"/></g>')
    return ''.join(out)


def m_graph(s):
    """A small graph: the shortest path lights up, node by node."""
    total = 6
    nodes = {'a': (292, 104), 'b': (314, 52), 'c': (340, 98), 'd': (364, 46), 'e': (390, 90), 'f': (352, 124)}
    edges, path = ['ab', 'ac', 'bc', 'bd', 'cd', 'ce', 'de', 'cf', 'fe'], ['ac', 'cd', 'de']
    out = [f'<path d="{"".join(f"M{nodes[u][0]} {nodes[u][1]}L{nodes[v][0]} {nodes[v][1]}" for u, v in edges)}" stroke="#fff" stroke-opacity=".16" stroke-width="1.5" fill="none"/>']
    for i, (u, v) in enumerate(path):
        (x1, y1), (x2, y2) = nodes[u], nodes[v]
        length, name, a = math.hypot(x2 - x1, y2 - y1), s.uid('e'), .6 + i * .7
        s.css.append(f'.{name}{{stroke-dasharray:{n(length)};animation:{name} {total}s linear infinite}}@keyframes {name}{{0%,{a / total * 100:.2f}%{{stroke-dashoffset:{n(length)};opacity:1}}'
                     f'{(a + .6) / total * 100:.2f}%,85%{{stroke-dashoffset:0;opacity:1}}93%,100%{{stroke-dashoffset:0;opacity:0}}}}')
        out.append(f'<path class="{name}" d="M{x1} {y1}L{x2} {y2}" stroke="{lerp(VIVID, i / 2)}" stroke-width="3" stroke-linecap="round" fill="none"/>')
    lit = {'a': .5, 'c': 1.2, 'd': 1.9, 'e': 2.6}
    for i, (key, (x, y)) in enumerate(nodes.items()):
        out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#16161f" stroke="#fff" stroke-opacity=".3" stroke-width="1.5"/>')
        if key in lit:
            out.append(f'<circle cx="{x}" cy="{y}" r="6.5" fill="{lerp(VIVID, list(lit).index(key) / 3)}"{s.window(total, lit[key], 5.3 - lit[key])}/>')
    return ''.join(out)


TILES = [
    ('workstation', 'Workstation', ['22 tools in one place: algorithm', 'visualizers, math, crypto, games.'], 'workstation.pixel-cursor.com', m_sort),
    ('relentchess', 'RelentChess', ['Stockfish in your browser:', 'analysis, game review, puzzles.'], 'relentchess.pixel-cursor.com', m_chess),
    ('drinkbro', 'DrinkBro', ['Hydration tracker with water', 'that moves. Web and Android.'], 'drinkbro.pixel-cursor.com', m_water),
    ('iagree', 'I Have Read and Agree', ['A game about the fine print.', '20 forms, 20 dark patterns.'], 'iagree.pixel-cursor.com', m_agree),
    ('seatsketch', 'Seatsketch Studio', ['Seating plan editor: rooms,', 'tables, guests. Web and desktop.'], 'seatsketch.pixel-cursor.com', m_seats),
    ('youtube', 'PixelCursor on YouTube', ['Simulating things nobody asked for:', 'wild questions, run in real code.'], 'youtube.com/@PixelCursor', m_graph),
]


def tiles():
    for i, (slug, name, lines, host, motif) in enumerate(TILES):
        s = Svg(410, 150, f'{name}. {" ".join(lines)} {host}')
        s.pad = (5, 0) if i % 2 else (0, 5)  # two tiles at 50 % each share a 10 px gutter and line up with the wide cards
        back = s.glow(410, 0, 230, 150, '#6e6ec8', .22) + s.glow(0, 150, 200, 110, '#f050f0', .1) + s.dots(pitch=12, r=.9, base=.6) + s.glow(120, 75, 250, 120, BG, .96)
        words = (s.text(name, 20, 45, 19, 'x', ls=-.4) + ''.join(s.text(line, 20, 69 + i * 18, 12, fill=DIM) for i, line in enumerate(lines))
                 + s.text('↗', 20, 127, 12, 'b', fill=ORANGE) + s.text(host, 36, 127, 11.5, fill=CREAM))
        s.add(s.card(back + words + motif(s), rx=10))
        s.save(f'assets/apps/{slug}.svg')


if __name__ == '__main__':
    hero()
    session()
    tiles()
