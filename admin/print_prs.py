"""Print all PRs in saved JSON file in Markdown list for CHANGELOG"""

import json

with open("prs2.json") as f:
    for pr in sorted(json.load(f), key=lambda k: k["merged_at"], reverse=True):
        if not pr["title"].startswith("Bump"):
            id = pr["url"].replace(
                "https://api.github.com/repos/RDFLib/rdflib/pulls/", ""
            )
            u = f"https://github.com/RDFLib/rdflib/pull/{id}"
            print(f"""* {pr['title']}\n  [PR #{id}]({u})""")
