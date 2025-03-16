# codeforces_analyzer.py
import os
import time
import pandas as pd
import schedule
import argparse
from datetime import datetime
from rich.table import Table
from rich import print
from utils.api import fetch_user_submissions, fetch_user_rating, fetch_problemset
from utils.analysis import analyze_weaknesses, is_optimal_difficulty
from utils.slack import SlackManager
from utils.rating import get_rating_tier
from utils.goals import get_next_milestone

# Initialize Slack Manager
slack_manager = SlackManager()

def recommend_problems(weak_tags: list, current_rating: int) -> list:
    """Recommend problems based on weak tags and optimal difficulty range."""
    problems = fetch_problemset()
    recommendations = []
    
    for problem in problems:
        if "rating" not in problem:
            continue
            
        problem_rating = problem["rating"]
        tags = problem.get("tags", [])
        
        if (is_optimal_difficulty(problem_rating, current_rating) and 
            any(tag in weak_tags for tag in tags)):
            recommendations.append({
                "contestId": problem["contestId"],
                "index": problem["index"],
                "name": problem["name"],
                "rating": problem_rating,
                "tags": ", ".join(tags),
                "url": f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}"
            })
    
    # Sort by closest to current rating
    return sorted(recommendations, 
                 key=lambda x: abs(x["rating"] - current_rating))[:5]

def save_daily_progress(username: str, weaknesses: dict, recommendations: list):
    """Save daily stats to CSV."""
    date_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"progress_{username}.csv"
    
    weak_tags = list(weaknesses.keys())[:3]
    weak_acc = [f"{weaknesses[tag]['accuracy']:.1f}%" for tag in weak_tags]
    rec_problems = [f"{p['contestId']}{p['index']}" for p in recommendations]
    
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("date,weak_tag1,weak_tag2,weak_tag3,accuracy1,accuracy2,accuracy3,recommended_problems\n")
    
    with open(filename, "a") as f:
        f.write(f"{date_str},{','.join(weak_tags)},{','.join(weak_acc)},{'|'.join(rec_problems)}\n")

def plot_progress(username: str):
    """Generate progress plot using matplotlib."""
    import matplotlib.pyplot as plt
    df = pd.read_csv(f"progress_{username}.csv")
    if len(df) < 2:
        return
    
    plt.figure(figsize=(10, 5))
    for i in range(1, 4):
        tag = df[f"weak_tag{i}"].iloc[-1]
        acc = df[f"accuracy{i}"].str.replace("%", "").astype(float)
        plt.plot(df["date"], acc, marker="o", label=f"{tag}")
    
    plt.title("Accuracy Trend for Weak Tags")
    plt.xlabel("Date")
    plt.ylabel("Accuracy (%)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"progress_{username}.png")
    plt.close()

def display_dashboard(username: str, weaknesses: dict, recommendations: list, current_rating: int):
    """Rich CLI Dashboard"""
    # Weaknesses Table
    table = Table(title=f"[bold cyan]{username}'s Weak Areas[/bold cyan]")
    table.add_column("Tag", style="magenta")
    table.add_column("Accuracy (%)", justify="right")
    table.add_column("Total Attempted", justify="right")
    
    for tag, stats in list(weaknesses.items())[:5]:
        table.add_row(tag, f"{stats['accuracy']:.1f}%", str(stats["total"]))
    
    # Recommendations Table
    rec_table = Table(title="[bold green]Today's Recommended Problems[/bold green]")
    rec_table.add_column("ID", style="yellow")
    rec_table.add_column("Name")
    rec_table.add_column("Rating", justify="right")
    rec_table.add_column("Tags")
    rec_table.add_column("URL")
    
    for problem in recommendations:
        diff_status = "✅" if is_optimal_difficulty(problem["rating"], current_rating) else "💪"
        rec_table.add_row(
            f"{problem['contestId']}{problem['index']}",
            problem["name"],
            f"{problem['rating']} {diff_status}",
            problem["tags"],
            f"[link={problem['url']}]{problem['url']}[/link]"
        )
    
    print(table)
    print(rec_table)

def daily_job():
    username = "praveenkumarcdm2001"  # Hardcode or fetch from .env
    
    # Fetch data
    submissions_df = fetch_user_submissions(username)
    current_rating = fetch_user_rating(username)
    weaknesses = analyze_weaknesses(submissions_df)
    weak_tags = list(weaknesses.keys())[:3]
    recommendations = recommend_problems(weak_tags, current_rating)
    
    # Save and plot
    save_daily_progress(username, weaknesses, recommendations)
    plot_progress(username)
    
    # CLI Dashboard
    display_dashboard(username, weaknesses, recommendations, current_rating)
    
    # Slack Notification
    current_title = get_rating_tier(current_rating)
    next_milestone, points_needed = get_next_milestone(current_rating)
    
    message = (
        f"*🏆 Codeforces Daily Report for {username}*\n"
        f"Current Rating: {current_rating} ({current_title})\n"
        f"Next Milestone: {points_needed} points to {next_milestone}\n\n"
        "*🔍 Weak Areas:*\n" + 
        "\n".join([f"- {tag} ({stats['accuracy']:.1f}%)" 
                  for tag, stats in list(weaknesses.items())[:3]]) + "\n\n"
        "*📚 Recommended Problems:*\n" +
        "\n".join([f"- <{p['url']}|{p['name']}> ({p['rating']} rating)" 
                  for p in recommendations])
    )
    
    slack_manager.send_message(message)
    slack_manager.send_file("📈 Progress Plot", f"progress_{username}.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true", help="Run job immediately")
    parser.add_argument("--test", action="store_true", help="Test mode (runs every 5 min)")
    args = parser.parse_args()
    
    if args.run_now:
        daily_job()
    
    # Configure scheduler
    if args.test:
        schedule.every(5).minutes.do(daily_job)
    else:
        schedule.every().day.at("08:00").do(daily_job)
    
    print("AI Coach is running... (Ctrl+C to exit)")
    while True:
        schedule.run_pending()
        time.sleep(60)