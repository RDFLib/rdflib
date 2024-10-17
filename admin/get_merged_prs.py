"""Get all merged PRs since last release, save them to a JSON file"""

import json
import urllib.request
import urllib.parse

# https://api.github.com/search/issues?q=repo:rdflib/rdflib+is:pr+merged:%3E=2023-08-02&per_page=300&page=1
LAST_RELEASE_DATE = "2023-08-02"
ISSUES_URL = "https://api.github.com/search/issues"
ITEMS = []
PAGE = 1

# make sequential requests for each page of PRs
while True:
    params = {
        "q": f"repo:rdflib/rdflib+is:pr+merged:>={LAST_RELEASE_DATE}",
        "per_page": 100,
        "page": PAGE,
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = ISSUES_URL + "?" + query_string

    print(f"Getting {url}")
    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        link_headers = response.info()["link"].split(",")

    json_data = json.loads(response_text)
    ITEMS.extend(json_data["items"])

    keep_going = False
    for link in link_headers:
        if 'rel="next"' in link:
            # url = link.strip("<").split(">")[0]
            PAGE += 1
            keep_going = True

    if not keep_going:
        break

with open("merged_prs.json", "w") as f:
    json.dump(ITEMS, f, indent=4)

# split interesting and boring PRs into two lists
good_prs = []
boring_prs = []
for pr in sorted(ITEMS, key=lambda k: k["closed_at"], reverse=True):
    matches = ["bump", "pre-commit.ci"]
    if any(x in pr["title"] for x in matches):
        boring_prs.append(
            f"""* {pr['closed_at'][:10]} - {pr['title']}\n  [PR #{pr['number']}]({pr['html_url']})"""
        )
    else:
        good_prs.append(
            f"""* {pr['closed_at'][:10]} - {pr['title']}\n  [PR #{pr['number']}]({pr['html_url']})"""
        )

for pr in good_prs:
    print(pr)

print()
print()

for pr in boring_prs:
    print(pr)
