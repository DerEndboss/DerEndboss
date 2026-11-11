"""Refresh assets/grind.svg: the contribution calendar of the last twelve months.

Runs daily in GitHub Actions (see .github/workflows/stats.yml). Uses only the
contribution counts GitHub already shows on the profile. Standard library only.

Local run:  GH_TOKEN=$(gh auth token) python3 scripts/update_stats.py
Offline:    PROFILE_STATS_FILE=fixture.json python3 scripts/update_stats.py
"""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from kit import BG, CREAM, DIM, INK, ORANGE, W, Svg, n

OWNER = os.environ.get('PROFILE_OWNER', 'DerEndboss')
QUERY = '''query($login:String!) { user(login:$login) { contributionsCollection { contributionCalendar {
 totalContributions weeks { contributionDays { contributionCount date } } } } } }'''
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
    return data['data']['user']['contributionsCollection']['contributionCalendar']


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
    render(json.loads(Path(fixture).read_text()) if fixture else fetch())
