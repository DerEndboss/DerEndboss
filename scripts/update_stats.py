"""Refresh public profile counters and activity. Uses only public GitHub data."""
import json, os, urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
OWNER=os.environ.get('PROFILE_OWNER','DerEndboss')
QUERY='''query($login:String!,$cursor:String) { user(login:$login) {
 followers { totalCount }
 repositories(privacy:PUBLIC,ownerAffiliations:OWNER,first:100,after:$cursor) {
 totalCount nodes { stargazerCount } pageInfo { hasNextPage endCursor }
 }
 contributionsCollection { contributionCalendar { totalContributions weeks {
 contributionDays { contributionCount date }
 } } }
} }'''
def fetch():
 token=os.environ['GH_TOKEN'];cursor=None;stars=0;first=None
 while True:
  data=json.dumps({'query':QUERY,'variables':{'login':OWNER,'cursor':cursor}}).encode()
  req=urllib.request.Request('https://api.github.com/graphql',data=data,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','User-Agent':'profile-stats'})
  with urllib.request.urlopen(req,timeout=30) as r: response=json.load(r)
  if response.get('errors'):raise RuntimeError(response['errors'])
  user=response['data']['user']
  if first is None:first=user
  repos=user['repositories'];stars+=sum(n['stargazerCount'] for n in repos['nodes'])
  if not repos['pageInfo']['hasNextPage']:break
  cursor=repos['pageInfo']['endCursor']
 return first,stars

def render(user,stars):
 ASSETS.mkdir(exist_ok=True)
 cal=user['contributionsCollection']['contributionCalendar']
 colors=['#342A27','#674033','#985239','#C96D49','#F19B71']
 metrics=[('LAST 12 MONTHS',cal['totalContributions']),('FOLLOWERS',user['followers']['totalCount']),('STARS',stars),('PUBLIC REPOS',user['repositories']['totalCount'])]
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="150" viewBox="0 0 1120 150" role="img" aria-label="Public GitHub statistics"><rect width="1120" height="150" fill="#1F1C1C"/>']
 for i,(label,value) in enumerate(metrics):
  x=i*280
  parts.append(f'<rect x="{x+3}" y="3" width="271" height="144" rx="6" fill="#292323" stroke="#574039"/><rect x="{x+3}" y="3" width="271" height="3" fill="#D97A58"/><text x="{x+140}" text-anchor="middle" y="43" fill="#B59C8D" font-family="monospace" font-size="14" letter-spacing="1">{label}</text><text x="{x+140}" text-anchor="middle" y="112" fill="#F5EDE0" font-family="monospace" font-size="52" font-weight="bold">{value:,}</text>')
 parts.append('</svg>');(ASSETS/'stats.svg').write_text(''.join(parts))
 year=datetime.now(timezone.utc).year
 days=[d for w in cal['weeks'] for d in w['contributionDays'] if d['date'].startswith(str(year))]
 year_total=sum(d['contributionCount'] for d in days)
 year_svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="126" viewBox="0 0 1120 126" role="img" aria-label="{year_total:,} contributions this year, {year}"><rect x="3" y="3" width="1114" height="120" rx="7" fill="#292323" stroke="#D97A58"/><text x="560" y="33" text-anchor="middle" fill="#B59C8D" font-family="monospace" font-size="16" letter-spacing="2">CONTRIBUTIONS THIS YEAR</text><text x="560" y="99" text-anchor="middle" fill="#F5EDE0" font-family="monospace" font-size="55" font-weight="bold">{year_total:,}</text><text x="1080" y="34" text-anchor="end" fill="#D97A58" font-family="monospace" font-size="14">{year}</text><rect x="25" y="119" width="60" height="2" fill="#D97A58"><animate attributeName="x" values="25;1035;25" dur="12s" repeatCount="indefinite"/></rect></svg>'
 (ASSETS/'year.svg').write_text(year_svg)

 weeks=cal['weeks'];startx=56;step=19;cell=14
 peak=max((d['contributionCount'] for w in weeks for d in w['contributionDays']),default=1)
 def intensity(n):return 0 if not n else min(4,1+int(n/max(1,peak)*3))
 p=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="275" viewBox="0 0 1120 275" role="img" aria-label="Contribution calendar for the last year"><rect x="1" y="1" width="1118" height="273" rx="6" fill="#1F1C1C" stroke="#574039"/><text x="30" y="37" font-size="17" font-family="monospace" letter-spacing="2" fill="#F5EDE0">THE GRIND</text><text x="1090" y="37" text-anchor="end" font-family="monospace" font-size="13" fill="#B59C8D">LAST 12 MONTHS</text>']
 month=''
 for w,week in enumerate(weeks):
  first=week['contributionDays'][0]['date'];m=first[5:7]
  if m!=month:
   month=m;p.append(f'<text x="{startx+w*step}" y="67" font-family="monospace" font-size="10" fill="#B59C8D">{datetime.fromisoformat(first).strftime("%b").upper()}</text>')
  for day in week['contributionDays']:
   weekday=(datetime.fromisoformat(day['date']).weekday()+1)%7
   n=day['contributionCount'];x=startx+w*step;y=82+weekday*step
   p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{colors[intensity(n)]}"><title>{day["date"]}: {n} contributions</title></rect>')
 # A little moving orange spark tracks across the calendar; counts stay unchanged.
 p.append(f'<rect x="{startx}" y="228" width="14" height="3" fill="#D97A58"><animate attributeName="x" values="{startx};{startx+(len(weeks)-1)*step};{startx}" dur="12s" repeatCount="indefinite"/></rect>')
 p.append(f'<text x="30" y="257" fill="#D97A58" font-family="monospace" font-size="13">{cal["totalContributions"]:,} CONTRIBUTIONS</text>')
 for i,c in enumerate(colors):p.append(f'<rect x="{970+i*21}" y="244" width="14" height="14" rx="2" fill="{c}"/>')
 p.append('</svg>');(ASSETS/'activity.svg').write_text(''.join(p))

if __name__=='__main__':
 fixture=os.environ.get('PROFILE_STATS_FILE')
 if fixture:
  user=json.loads(Path(fixture).read_text())['data']['user']
  stars=sum(n['stargazerCount'] for n in user['repositories']['nodes'])
 else:user,stars=fetch()
 render(user,stars)
 print('Updated public profile counters and contribution calendar.')
