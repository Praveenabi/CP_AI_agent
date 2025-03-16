# utils/goals.py
from typing import Tuple

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

def get_next_milestone(current_rating: int) -> Tuple[str, int]:
    """Returns (next_milestone_title, points_needed)."""
    sorted_tiers = sorted(RATING_TIERS.items(), key=lambda x: x[0])
    for threshold, title in sorted_tiers:
        if current_rating < threshold:
            return (title, threshold - current_rating)
    return ("Legendary Grandmaster", 3000 - current_rating)