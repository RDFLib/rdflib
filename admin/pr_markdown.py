import json
import sys
from dataclasses import dataclass


@dataclass
class PR:
    number: int
    title: str
    pull_request_merged_at: str
    pull_request_url: str
    username: str

    def __repr__(self):
        return f"{self.title} by @{self.username} in [#{self.number}]({self.pull_request_url})"


try:
    json_data = json.load(sys.stdin)
    prs = [PR(**pr) for pr in json_data["items"]]
    for pr in prs:
        print(f"- {pr}")
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
