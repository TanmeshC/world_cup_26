"""Validate the analytics pipeline end-to-end."""

from utils.analytics import get_analytics
from utils.qualified_teams_2026 import get_qualified_teams
from models.match_predictor import MatchPredictor

print("Loading analytics pipeline...")
data = get_analytics()

teams = get_qualified_teams()
print(f"2026 qualified teams: {len(teams)}")
print(f"Historical matches: {len(data['matches'])}")

elo = data["elo"].get_2026_ratings()
print(f"\nTop 5 Elo (2026 teams):\n{elo.head()}")

power = data["power_rankings"]
print(f"\nTop 5 Power Index:\n{power[['rank','team','power_index']].head()}")

features = data["engineer"].build_match_features()
predictor = MatchPredictor(features).train()
print(f"\nMatch predictor CV accuracy: {predictor.cv_accuracy:.1%}")

print("\nPipeline OK.")
