from typing import Dict
import pandas as pd

def analyze_weaknesses(submissions_df: pd.DataFrame) -> Dict:
    """Calculate accuracy per problem tag."""
    tag_stats = {}
    for _, row in submissions_df.iterrows():
        for tag in row["tags"]:
            tag_stats.setdefault(tag, {"total": 0, "correct": 0})
            tag_stats[tag]["total"] += 1
            if row["verdict"] == "OK":
                tag_stats[tag]["correct"] += 1
    
    weaknesses = {}
    for tag, stats in tag_stats.items():
        accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
        weaknesses[tag] = {"accuracy": accuracy, "total": stats["total"]}
    
    return dict(sorted(weaknesses.items(), key=lambda x: x[1]["accuracy"]))


def is_optimal_difficulty(problem_rating: int, user_rating: int) -> bool:
    """
    Checks if problem rating is within ±200 of user's current rating.
    Optimal range for improvement (Codeforces community heuristic).
    """
    if problem_rating == 0:  # Unrated problems
        return False
    return abs(problem_rating - user_rating) <= 200