# utils/rating.py
from typing import Dict

def simulate_rating_change(
    solved_count: int, 
    expected_solved: float, 
    current_rating: int
) -> int:
    """
    Simulates Codeforces-like rating changes.
    Formula inspired by Codeforces' Elo-MMR system (simplified).
    """
    # Codeforces uses a K-factor between 80-100 for most users
    k_factor = 80 if current_rating < 2400 else 40  # Reduced volatility for high ratings
    
    # Calculate performance difference
    performance_diff = solved_count - expected_solved
    
    # Rating change formula
    delta = k_factor * performance_diff
    
    # Cap maximum delta for stability
    delta = max(min(delta, 150), -150)
    
    return int(current_rating + delta)

def get_rating_tier(rating: int) -> str:
    """Convert rating to Codeforces title (e.g., 2100 → 'Master')."""
    RATING_TIERS = {
        1200: "Pupil",
        1400: "Specialist",
        1600: "Expert",
        1900: "Candidate Master",
        2100: "Master",
        2300: "International Master",
        2400: "Grandmaster",
        2600: "International Grandmaster",
        3000: "Legendary Grandmaster"
    }
    for threshold, title in sorted(RATING_TIERS.items(), reverse=True):
        if rating >= threshold:
            return title
    return "Newbie"