import pandas as pd
import numpy as np

from utils.qualified_teams_2026 import get_qualified_teams


class FeatureEngineer:
    def __init__(self, matches_df, elo_engine=None):
        self.matches = matches_df
        self.elo = elo_engine

    def build_team_statistics(self):
        """Aggregate historical WC stats for all teams (training use)."""
        teams = set(self.matches["home_team"].dropna()) | set(
            self.matches["away_team"].dropna()
        )
        results = []
        for team in teams:
            home = self.matches[self.matches["home_team"] == team]
            away = self.matches[self.matches["away_team"] == team]
            goals_for = home["home_score"].sum() + away["away_score"].sum()
            goals_against = home["away_score"].sum() + away["home_score"].sum()
            wins = (
                (home["home_score"] > home["away_score"]).sum()
                + (away["away_score"] > away["home_score"]).sum()
            )
            results.append({
                "team": team,
                "matches": len(home) + len(away),
                "wins": wins,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_diff": goals_for - goals_against,
                "win_rate": wins / max(len(home) + len(away), 1),
            })
        return pd.DataFrame(results)

    def build_match_features(self):
        """Build per-match feature matrix for ML training."""
        df = self.matches.dropna(subset=["home_team", "away_team"]).copy()
        stats = self.build_team_statistics().set_index("team")
        elo_map = {}
        if self.elo:
            elo_map = self.elo.ratings

        rows = []
        for _, m in df.iterrows():
            h, a = m["home_team"], m["away_team"]
            h_stats = stats.loc[h] if h in stats.index else None
            a_stats = stats.loc[a] if a in stats.index else None
            h_elo = elo_map.get(h, 1500)
            a_elo = elo_map.get(a, 1500)
            rows.append({
                "home_team": h,
                "away_team": a,
                "year": m.get("Year"),
                "elo_diff": h_elo - a_elo,
                "home_elo": h_elo,
                "away_elo": a_elo,
                "home_win_rate": h_stats["win_rate"] if h_stats is not None else 0.5,
                "away_win_rate": a_stats["win_rate"] if a_stats is not None else 0.5,
                "home_goal_diff": h_stats["goal_diff"] if h_stats is not None else 0,
                "away_goal_diff": a_stats["goal_diff"] if a_stats is not None else 0,
                "home_won": int(m.get("home_score", 0) > m.get("away_score", 0)),
            })
        return pd.DataFrame(rows)

    def get_2026_team_features(self):
        """Feature vectors for 2026 teams only — used in predictions."""
        stats = self.build_team_statistics()
        qualified = get_qualified_teams()
        return stats[stats["team"].isin(qualified)].copy()
