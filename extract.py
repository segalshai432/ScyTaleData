import os
import json
import requests
from pathlib import Path


##Change to your GitHub token 
GITHUB_TOKEN = "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"
GITHUB_ORG = "Scytale-exercise"
REPO = "Scytale-exercise"


if not GITHUB_TOKEN or not GITHUB_ORG or not REPO:
    raise ValueError("GITHUB_TOKEN, GITHUB_ORG, and REPO environment variables must be set.")

API_BASE = "https://api.github.com"

# Output directory->This must be changed to your desired output directory
RAW_DIR = Path("C:/Users/segal/OneDrive/Desktop")
RAW_DIR.mkdir(parents=True, exist_ok=True)




def github_request(url, params=None):
    #Handles authenticated GitHub API requests.
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} → {response.text}")
    return response.json()


def get_merged_pull_requests(org, repo):
    #Fetch merged pull requests for a single repository.
    url = f"{API_BASE}/repos/{org}/{repo}/pulls"
    merged_prs = []
    page = 1

    while True:
        prs = github_request(url, params={"state": "closed", "per_page": 100, "page": page})
        if not prs:
            break

        for pr in prs:
            if pr.get("merged_at"):
                merged_prs.append(pr)
        page += 1

    return merged_prs


# Main logic

def main():
    print(f" Authenticating with GitHub for repo: {REPO}...")
    print(f" Fetching merged PRs from {REPO}...")
    merged_prs = get_merged_pull_requests(GITHUB_ORG, REPO)

    all_prs = []
    for pr in merged_prs:
        all_prs.append({
            "repo": REPO,
            "number": pr["number"],
            "title": pr["title"],
            "user": pr["user"]["login"],
            "merged_at": pr["merged_at"],
            "merged_by": pr.get("merged_by", {}).get("login"),
            "url": pr["html_url"],
        })

    # Save results 
    output_path = RAW_DIR / "pull_requests.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_prs, f, indent=2)

    print(f"Results Saved {len(all_prs)} merged PRs → {output_path}")


if __name__ == "__main__":
    main()
