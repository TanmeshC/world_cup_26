"""
Composite power index combining Elo, FIFA ranking points, and historical WC performance.
All exported rankings are restricted to 2026-qualified teams.
"""

import pandas as pd
import numpy as np

from utils.qualified_teams_2026 import get_qualified_teams, restrict_team_list


def _normalize_series(s, higher_is_better=True):
    s = s.astype(float)
    if s.max() == s.min():
        return pd.Series(0.5, index=s.index)
    normed = (s - s.min()) / (s.max() - s.min())
    return normed if higher_is_better else 1 - normed


class PowerIndex:
    WEIGHTS = {
        "elo": 0.40,
        "fifa_points": 0.30,
        "wc_wins": 0.15,
        "wc_appearances": 0.10,
        "recent_form": 0.05,
    }

    def __init__(self, elo_ratings_df, fifa_rankings_df, matches_df):
        self.elo = elo_ratings_df
        self.fifa = fifa_rankings_df
        self.matches = matches_df

    def _wc_stats(self):
        teams = get_qualified_teams()
        records = []
        for team in teams:
            home = self.matches[self.matches["home_team"] == team]
            away = self.matches[self.matches["away_team"] == team]
            wins = 0
            for _, m in home.iterrows():
                if m.get("home_score", 0) > m.get("away_score", 0):
                    wins += 1
            for _, m in away.iterrows():
                if m.get("away_score", 0) > m.get("home_score", 0):
                    wins += 1
            records.append({
                "team": team,
                "wc_matches": len(home) + len(away),
                "wc_wins": wins,
            })
        return pd.DataFrame(records)

    def _recent_form(self, last_n_years=3):
        teams = get_qualified_teams()
        max_year = self.matches["Year"].max()
        cutoff = max_year - last_n_years
        recent = self.matches[self.matches["Year"] >= cutoff]
        records = []
        for team in teams:
            pts = 0
            for _, m in recent.iterrows():
                if m["home_team"] == team:
                    hs, as_ = m.get("home_score", 0), m.get("away_score", 0)
                    if hs > as_:
                        pts += 3
                    elif hs == as_:
                        pts += 1
                elif m["away_team"] == team:
                    hs, as_ = m.get("home_score", 0), m.get("away_score", 0)
                    if as_ > hs:
                        pts += 3
                    elif as_ == hs:
                        pts += 1
            records.append({"team": team, "recent_points": pts})
        return pd.DataFrame(records)

    def compute(self):
        teams = get_qualified_teams()
        elo_map = self.elo.set_index("team")["elo"].to_dict()
        fifa_df = self.fifa.copy()
        fifa_df["team"] = fifa_df["team"].str.strip()
        fifa_map = fifa_df.set_index("team")["points"].to_dict()
        wc_stats = self._wc_stats()
        form = self._recent_form()

        rows = []
        for team in teams:
            rows.append({
                "team": team,
                "elo": elo_map.get(team, 1500),
                "fifa_points": fifa_map.get(team, 0),
                "wc_wins": wc_stats.loc[wc_stats["team"] == team, "wc_wins"].values[0]
                if team in wc_stats["team"].values else 0,
                "wc_matches": wc_stats.loc[wc_stats["team"] == team, "wc_matches"].values[0]
                if team in wc_stats["team"].values else 0,
                "recent_points": form.loc[form["team"] == team, "recent_points"].values[0]
                if team in form["team"].values else 0,
            })

        df = pd.DataFrame(rows)
        df["elo_norm"] = _normalize_series(df["elo"])
        df["fifa_norm"] = _normalize_series(df["fifa_points"])
        df["wc_wins_norm"] = _normalize_series(df["wc_wins"])
        df["wc_matches_norm"] = _normalize_series(df["wc_matches"])
        df["form_norm"] = _normalize_series(df["recent_points"])

        df["power_index"] = (
            self.WEIGHTS["elo"] * df["elo_norm"]
            + self.WEIGHTS["fifa_points"] * df["fifa_norm"]
            + self.WEIGHTS["wc_wins"] * df["wc_wins_norm"]
            + self.WEIGHTS["wc_appearances"] * df["wc_matches_norm"]
            + self.WEIGHTS["recent_form"] * df["form_norm"]
        ) * 100

        df = df.sort_values("power_index", ascending=False).reset_index(drop=True)
        df["rank"] = range(1, len(df) + 1)
        return df
