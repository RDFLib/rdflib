"""Get all merged PRs since last release, save them to a JSON file"""

import httpx
import json
from datetime import datetime


r = httpx.get(
    "https://api.github.com/repos/rdflib/rdflib/pulls",
    params={
        "state": "closed",
        "per_page": 100,
        "page": 0,  # must get all pages up to date of last release
    },
)
prs = []
if r.status_code == 200:
    for pr in r.json():
        if pr["merged_at"] is not None:
            d = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ")
            if isinstance(d, datetime):
                if d > datetime.strptime("2021-10-10", "%Y-%m-%d"):
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
