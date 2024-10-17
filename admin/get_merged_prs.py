"""Get all merged PRs since last release, save them to a JSON file"""

import json
from datetime import datetime

import httpx

r = httpx.get(
    "https://api.github.com/repos/rdflib/rdflib/pulls",
    params={
        "state": "closed",
        "per_page": 100,
        "page": 0,  # must get all pages up to date of last release
        #"sort": "updated",
    },
)
prs = []
if r.status_code == 200:
    print(len(r.json()))
    for pr in r.json():
        if pr["merged_at"] is not None:
            d = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ")
            if isinstance(d, datetime):
                if d > datetime.strptime("2023-08-02", "%Y-%m-%d"):
                    prs.append(
                        {
                            "url": pr["url"],
                            "title": pr["title"],
                            "merged_at": pr["merged_at"],
                        }
                    )
    with open("prs.json", "w") as f:
        json.dump(sorted(prs, key=lambda d: d["merged_at"], reverse=True), f)
else:
    print("ERROR")


# 243 merged PRs
# https://api.github.com/search/issues?q=repo:rdflib/rdflib+is:pr+merged:%3E=2023-08-02&per_page=300&page=1
# https://api.github.com/search/issues?q=repo:rdflib/rdflib+is:pr+merged:%3E=2023-08-02&per_page=300&page=2
# https://api.github.com/search/issues?q=repo:rdflib/rdflib+is:pr+merged:%3E=2023-08-02&per_page=300&page=3
