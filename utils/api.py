# utils/api.py
import requests
import pandas as pd
from typing import Dict, List

def fetch_user_submissions(username: str) -> pd.DataFrame:
    """Fetch all Codeforces submissions for a user."""
    url = f"https://codeforces.com/api/user.status?handle={username}&count=1000"
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    if data["status"] != "OK":
        raise ValueError("Failed to fetch submissions")
    
    submissions = []
    for sub in data["result"]:
        if "problem" not in sub:
            continue
        problem = sub["problem"]
        submissions.append({
            "problem_id": f"{problem['contestId']}{problem['index']}",
            "tags": problem.get("tags", []),
            "rating": problem.get("rating", 0),
            "verdict": sub.get("verdict", ""),
            "time": pd.to_datetime(sub["creationTimeSeconds"], unit="s")
        })
    
    return pd.DataFrame(submissions)

def fetch_user_rating(username: str) -> int:
    """Fetch current Codeforces rating."""
    url = f"https://codeforces.com/api/user.info?handles={username}"
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    if data["status"] != "OK":
        raise ValueError("Failed to fetch user rating")
    
    return data["result"][0].get("rating", 1400)  # Default to 1400 if unrated

def fetch_problemset() -> List[Dict]:
    """Fetch all Codeforces problems for recommendations."""
    url = "https://codeforces.com/api/problemset.problems"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["result"]["problems"]

def fetch_contest_problems(contest_id: int) -> List[Dict]:
    """Fetch problems from a specific contest (for virtual contests)."""
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["result"]["problems"]

def fetch_past_contests(min_rating: int, max_rating: int) -> List[Dict]:
    """Fetch past contests filtered by average problem rating."""
    url = "https://codeforces.com/api/contest.list"
    response = requests.get(url).json()
    
    valid_contests = []
    for contest in response["result"]:
        if contest["phase"] == "FINISHED":
            problems = fetch_contest_problems(contest["id"])
            ratings = [p.get("rating", 0) for p in problems]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            if min_rating <= avg_rating <= max_rating:
                valid_contests.append(contest)
    return valid_contests