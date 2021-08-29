"""Get all merged PRs since last release, save them to a JSON file"""

import httpx
import json


r = httpx.get(
    "https://api.github.com/repos/rdflib/rdflib/pulls",
    params={
        "state": "closed",
        "per_page": 100,
        "page": 2,  # must get all pages up to date of last release
    },
)
prs = []
if r.status_code == 200:
    for pr in r.json():
        if pr["merged_at"] is not None:
            prs.append(
                {
                    "url": pr["url"],
                    "title": pr["title"],
                    "merged_at": pr["merged_at"],
                }
            )
    with open("prs2.json", "w") as f:
        json.dump(prs, f)
else:
    print("ERROR")
