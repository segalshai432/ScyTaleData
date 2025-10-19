import os
import json
import requests
import pandas as pd
from pathlib import Path

#Details for GitHub access:User must change these to their own details
GITHUB_TOKEN = "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"
GITHUB_ORG = "Scytale-exercise"
REPO = "Scytale-exercise"
API_BASE = "https://api.github.com"

# File paths:User must change these paths to their own desired paths
INPUT_FILE = Path("C:/Users/segal/OneDrive/Desktop/pull_requests.json")
OUTPUT_FILE = Path("C:/Users/segal/OneDrive/Desktop/pull_request_report.csv")



def github_request(url, params=None):
    #Handles authenticated GitHub API requests.
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"GitHub API error {response.status_code}: {response.text}")
    return response.json()

def check_if_approved(org, repo, pr_number):
    #Return True if PR was approved by at least one reviewer.
    url = f"{API_BASE}/repos/{org}/{repo}/pulls/{pr_number}/reviews"
    reviews = github_request(url)
    for r in reviews:
        if r.get("state", "").lower() == "approved":
            return True
    return False

def check_status_checks(org, repo, pr):
    """Return True if all required status checks passed before merge."""
    sha = pr.get("merge_commit_sha")
    if not sha:
        return False
    url = f"{API_BASE}/repos/{org}/{repo}/commits/{sha}/status"
    status_data = github_request(url)
    return status_data.get("state") == "success"

# ===== MAIN PROCESS =====
def main():
    print(" Loading PR data")
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        prs = json.load(f)

    print(f" Processing {len(prs)} pull requests...")

    results = []
    for pr in prs:
        number = pr["number"]
        print(f"  Checking PR #{number} - {pr['title']}")

        approved = check_if_approved(GITHUB_ORG, REPO, number)
        checks_passed = check_status_checks(GITHUB_ORG, REPO, pr)

        

        results.append({
    "PR Number": number,
     "Title": pr["title"],
    "Author": pr["user"],
    "Merged At": pr["merged_at"],
    "CR_Passed": approved,
    "CHECKS_PASSED": checks_passed
        })

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f" Report generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
