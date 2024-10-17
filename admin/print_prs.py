"""Print all PRs in saved JSON file in Markdown list for CHANGELOG"""


import json

with open("prs-raw.json") as f:
    json = json.load(f)
    prs = json["items"]
    good_prs = []
    boring_prs = []
    for pr in sorted(prs, key=lambda k: k["closed_at"], reverse=True):
        if "bump" in pr['title']:
            boring_prs.append(f"""* {pr['closed_at'][:10]} - {pr['title']}\n  [PR #{pr['number']}]({pr['html_url']})""")
        else:
            good_prs.append(f"""* {pr['closed_at'][:10]} - {pr['title']}\n  [PR #{pr['number']}]({pr['html_url']})""")

for pr in good_prs:
    print(pr)

print()
print()


for pr in boring_prs:
    print(pr)
