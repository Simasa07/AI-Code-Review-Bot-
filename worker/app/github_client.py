import os
import requests

GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


def _headers(accept: str = "application/vnd.github+json") -> dict:
    headers = {"Accept": accept}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def get_pr_diff(repo_full_name: str, pr_number: int) -> str:
    """Fetches the raw code diff (the actual code changes) for a pull request."""
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/pulls/{pr_number}"
    response = requests.get(
        url, headers=_headers(accept="application/vnd.github.v3.diff"), timeout=10
    )
    response.raise_for_status()
    return response.text


def post_pr_comment(repo_full_name: str, pr_number: int, body: str) -> None:
    """Posts a comment onto the pull request's conversation thread."""
    url = f"{GITHUB_API_URL}/repos/{repo_full_name}/issues/{pr_number}/comments"
    response = requests.post(url, headers=_headers(), json={"body": body}, timeout=10)
    response.raise_for_status()
