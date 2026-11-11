"""Refresh the data graphics: assets/grind.svg (contribution calendar of the last twelve
months) and assets/stats.svg (stars and profile views).

Runs daily in GitHub Actions (see .github/workflows/stats.yml). Uses the contribution counts
GitHub already shows on the profile, the stars of the public repositories and the number of
the view counter in the README. Standard library only.

Local run:  GH_TOKEN=$(gh auth token) python3 scripts/update_stats.py
Offline:    PROFILE_STATS_FILE=fixture.json python3 scripts/update_stats.py
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from kit import BG, CREAM, DIM, HOT, INK, ORANGE, ROOT, W, Svg, n

OWNER = os.environ.get('PROFILE_OWNER', 'DerEndboss')
QUERY = '''query($login:String!) { user(login:$login) {
 repositories(privacy:PUBLIC, ownerAffiliations:OWNER, first:100) { nodes { stargazerCount } }
 contributionsCollection { contributionCalendar {
 totalContributions weeks { contributionDays { contributionCount date } } } } } }'''
# the view counter: the README loads this badge once per visit, here we only read its number
COUNTER = 'https://visitor-badge.laobi.icu/badge?page_id=DerEndboss.profile.20261020.fresh'
CACHE = ROOT / 'assets/stats.json'
# magenta (a year ago) -> violet -> periwinkle (today), bright enough to read on black
DATA = [(0, '#f050f0'), (.3, '#c04df0'), (.55, '#8a5cf6'), (.8, '#7c83ff'), (1, '#aeb4ff')]
WALK = [(7, 0), (2, 1), (7, 1), (2, 2), (7, 2), (2, 3), (7, 3), (2, 4)]


def fetch():
    body = json.dumps({'query': QUERY, 'variables': {'login': OWNER}}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', data=body, headers={
        'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Content-Type': 'application/json', 'User-Agent': 'profile-stats'})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if data.get('errors'):
        raise RuntimeError(data['errors'])
    return data['data']['user']


def views(previous):
    """Number shown by the view counter; the last known value if the service does not answer."""
    try:
        req = urllib.request.Request(COUNTER, headers={'User-Agent': 'profile-stats'})
        with urllib.request.urlopen(req, timeout=20) as res:
            found = re.findall(r'>([\d,. ]+)</text>', res.read().decode())
        return max(previous, int(re.sub(r'\D', '', found[-1])))
    except Exception as err:  # the profile must not break because a badge service is down
        print('view counter not reachable:', err)
        return previous


def render_stats(stars, seen):
    s = Svg(W, 92, f'{stars:,} stars on public repositories, {seen:,} profile views.')
    s.css.append('.tw{animation:tw 3.2s ease-in-out infinite}@keyframes tw{0%,100%{transform:scale(1) rotate(0)}50%{transform:scale(1.18) rotate(12deg)}}'
                 '.bl{animation:bl 5s ease-in-out infinite}@keyframes bl{0%,44%,52%,100%{transform:scaleY(1)}48%{transform:scaleY(.08)}}')
    star = 'M0-11L3.2-3.6 11-3.4 4.9 1.6 7 9.2 0 4.9-7 9.2-4.9 1.6-11-3.4-3.2-3.6Z'
    icons = [f'<path class="tw" d="{star}" fill="{ORANGE}" stroke="{HOT}" stroke-width="1" stroke-linejoin="round"/>',
             '<g class="bl"><path d="M-13 0Q0-11 13 0Q0 11-13 0Z" fill="none" stroke="#9d9bff" stroke-width="2" stroke-linejoin="round"/><circle r="3.6" fill="#d2b0ff"/></g>']
    out = []
    for i, (value, label) in enumerate([(f'{stars:,}', 'STARS'), (f'{seen:,}', 'PROFILE VIEWS')]):
        wv, wl = s.width(value, 30), s.width(label, 10.5, 2.4)
        x = W / 4 + i * W / 2 - (26 + 14 + wv + 16 + wl) / 2
        out.append(f'<g transform="translate({n(x + 13)} 47)">{icons[i]}</g>' + s.text(value, x + 40, 58, 30, 'x', fill=CREAM)
                   + s.text(label, x + 40 + wv + 16, 53, 10.5, 'b', fill=DIM, ls=2.4))
    back = s.glow(0, 92, 330, 120, '#f050f0', .14) + s.glow(W, 0, 330, 120, '#6e6ec8', .18) + s.dots(base=.55) + s.glow(W / 2, 46, 420, 60, BG, .9)
    s.add(s.card(back + f'<rect x="{W / 2 - .5}" y="24" width="1" height="46" fill="#fff" fill-opacity=".1"/>' + ''.join(out)))
    s.save('assets/stats.svg')


def render(cal):
    weeks = cal['weeks'][-53:]
    year = datetime.now(timezone.utc).year
    this_year = sum(d['contributionCount'] for w in weeks for d in w['contributionDays'] if d['date'].startswith(str(year)))
    total = cal['totalContributions']
    peak = max((d['contributionCount'] for w in weeks for d in w['contributionDays']), default=1) or 1

    s = Svg(W, 252, f'The Grind. {total:,} contributions in the last twelve months, {this_year:,} of them in {year}. A Clawd follows the pixel hand along the calendar.')
    pitch, top, floor = 14.6, 82, 230
    left = (W - 52 * pitch) / 2
    ramp = s.gradient(DATA, left, top + 6 * pitch, left + 52 * pitch, top)

    quiet, loud, months, last = [], [], [], ''
    for col, week in enumerate(weeks):
        x = left + col * pitch
        first = week['contributionDays'][0]['date']
        if first[5:7] != last:
            last = first[5:7]
            if col < len(weeks) - 1:
                months.append(s.text(datetime.fromisoformat(first).strftime('%b').upper(), x - 4, 62, 9.5, 'b', fill=DIM, ls=1.6))
        for day in week['contributionDays']:
            row = (datetime.fromisoformat(day['date']).weekday() + 1) % 7  # Sunday on top, like GitHub
            count, y = day['contributionCount'], top + row * pitch
            if count:
                level = min(4, 1 + int(count / peak * 3.999))
                loud.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{[0, 2.7, 3.8, 4.9, 6][level]}"/>')
            else:
                quiet.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="1.3"/>')

    # the hand walks the calendar once, the Clawd keeps up, a soft beam lights the weeks they pass
    span, lap = W + 220, 30
    s.defs.append('<linearGradient id="beam" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/>'
                  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    s.css.append(f'.walk{{animation:walk {lap}s linear -9s infinite}}@keyframes walk{{from{{transform:translateX(-170px)}}to{{transform:translateX({span - 170}px)}}}}'
                 '.bob{animation:bob 1.2s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-4px)}}')
    walkers = (f'<g class="walk"><rect x="52" y="{top - 12}" width="76" height="{6 * pitch + 24}" fill="url(#beam)"/>'
               f'<g transform="translate(-48 {floor - 82})">{s.sprite("walk", WALK, .1)}</g>'
               f'<g transform="translate(84 {floor - 34})"><g class="bob">{s.hand(30)}</g></g></g>')

    head = (s.text('THE GRIND', 28, 38, 13, 'x', fill=INK, ls=3)
            + s.text(f'{this_year:,} IN {year}', W - 28, 38, 10.5, 'b', fill=DIM, anchor='end', ls=1.8)
            + s.text(f'{total:,}', 162, 38, 13, 'x', fill=CREAM) + s.text('CONTRIBUTIONS · LAST 12 MONTHS', 162 + s.width(f'{total:,}', 13) + 10, 38, 10.5, 'b', fill=DIM, ls=1.8))
    back = (s.glow(0, 252, 400, 200, '#f050f0', .16) + s.glow(W, 0, 400, 200, '#6e6ec8', .18) + s.glow(W / 2, 262, 430, 70, ORANGE, .12))
    line = f'<line x1="24" y1="{floor + 1}" x2="{W - 24}" y2="{floor + 1}" stroke="#2b2b3b" stroke-width="2" stroke-dasharray="10 10"/>'
    s.add(s.card(back + head + ''.join(months) + f'<g fill="#fff" fill-opacity=".14">{"".join(quiet)}</g><g fill="url(#{ramp})">{"".join(loud)}</g>' + line + walkers))
    s.save('assets/grind.svg')


if __name__ == '__main__':
    fixture = os.environ.get('PROFILE_STATS_FILE')
    user = json.loads(Path(fixture).read_text()) if fixture else fetch()
    render(user['contributionsCollection']['contributionCalendar'])
    known = json.loads(CACHE.read_text()) if CACHE.exists() else {'views': 0}
    counts = {'stars': sum(r['stargazerCount'] for r in user['repositories']['nodes']), 'views': known['views'] if fixture else views(known['views'])}
    CACHE.write_text(json.dumps(counts) + '\n')
    render_stats(counts['stars'], counts['views'])
