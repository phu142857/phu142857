import json, os, urllib.request
from datetime import date

LOGIN = "phu142857"
TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login:String!){
  user(login:$login){
    followers{totalCount}
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC){nodes{stargazerCount}}
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar{
        totalContributions
        weeks{contributionDays{date contributionCount}}
      }
    }
  }
}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
u = json.load(urllib.request.urlopen(req))["data"]["user"]
cc = u["contributionsCollection"]
cal = cc["contributionCalendar"]

days = [d for w in cal["weeks"] for d in w["contributionDays"]]
days.sort(key=lambda d: d["date"])

# current streak (bỏ qua hôm nay nếu chưa có contribution)
cur, i = 0, len(days) - 1
if days and days[i]["date"] == date.today().isoformat() and days[i]["contributionCount"] == 0:
    i -= 1
while i >= 0 and days[i]["contributionCount"] > 0:
    cur += 1
    i -= 1

# longest streak (trong 1 năm gần nhất)
longest = run = 0
for d in days:
    run = run + 1 if d["contributionCount"] > 0 else 0
    longest = max(longest, run)

stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])

rows = [
    ("⭐ Total Stars", stars),
    ("📝 Commits (1y)", cc["totalCommitContributions"]),
    ("🔀 Pull Requests", cc["totalPullRequestContributions"]),
    ("🐛 Issues", cc["totalIssueContributions"]),
    ("👥 Followers", u["followers"]["totalCount"]),
]
left = "".join(
    f'<text x="30" y="{70 + k*26}" class="lbl">{l}</text>'
    f'<text x="235" y="{70 + k*26}" class="val" text-anchor="end">{v}</text>'
    for k, (l, v) in enumerate(rows)
)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="215" viewBox="0 0 495 215">
<style>
  .t{{font:600 17px 'Segoe UI',Ubuntu,sans-serif;fill:#70a5fd}}
  .lbl{{font:400 13px 'Segoe UI',Ubuntu,sans-serif;fill:#a9b1d6}}
  .val{{font:700 13px 'Segoe UI',Ubuntu,sans-serif;fill:#c0caf5}}
  .big{{font:800 34px 'Segoe UI',Ubuntu,sans-serif}}
  .sm{{font:400 12px 'Segoe UI',Ubuntu,sans-serif;fill:#a9b1d6}}
</style>
<rect width="495" height="215" rx="6" fill="#1a1b27"/>
<text x="30" y="35" class="t">{LOGIN}'s GitHub Stats</text>
{left}
<line x1="270" y1="55" x2="270" y2="190" stroke="#3b4261"/>
<text x="382" y="95" class="big" text-anchor="middle" fill="#bb9af7">{cur}</text>
<text x="382" y="118" class="sm" text-anchor="middle">Current Streak 🔥</text>
<text x="382" y="160" class="big" text-anchor="middle" fill="#7dcfff">{longest}</text>
<text x="382" y="183" class="sm" text-anchor="middle">Longest Streak</text>
</svg>"""

os.makedirs("assets", exist_ok=True)
open("assets/stats.svg", "w", encoding="utf-8").write(svg)
