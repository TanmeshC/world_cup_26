"""
Elo rating engine trained on all World Cup matches (1930–2022).
Final ratings are exported only for 2026-qualified teams.
"""

import math
import pandas as pd

from utils.config import (
    ELO_INITIAL,
    ELO_K_GROUP,
    ELO_K_KNOCKOUT,
    ELO_K_FINAL,
    ELO_HOME_ADVANTAGE,
)
from utils.qualified_teams_2026 import restrict_team_list


def _expected_score(rating_a, rating_b):
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400))


def _actual_score(home_score, away_score, notes=""):
    """Return (home_result, away_result) as 1/0.5/0."""
    notes = str(notes) if pd.notna(notes) else ""
    if "penalty" in notes.lower() or "won on penalty" in notes.lower():
        # Penalty shootout — winner encoded in Score column or Notes
        if home_score > away_score:
            return 1.0, 0.0
        if away_score > home_score:
            return 0.0, 1.0
    if home_score > away_score:
        return 1.0, 0.0
    if away_score > home_score:
        return 0.0, 1.0
    return 0.5, 0.5


def _k_factor(round_name):
    r = str(round_name).lower() if pd.notna(round_name) else ""
    if "final" in r and "semi" not in r and "quarter" not in r:
        return ELO_K_FINAL
    if any(x in r for x in ("semi", "quarter", "round of", "knockout", "last 16", "last 32")):
        return ELO_K_KNOCKOUT
    return ELO_K_GROUP


class EloEngine:
    def __init__(self, initial_rating=ELO_INITIAL):
        self.initial_rating = initial_rating
        self.ratings = {}
        self.history = []

    def _get(self, team):
        return self.ratings.get(team, self.initial_rating)

    def process_matches(self, matches_df):
        df = matches_df.sort_values(["Year", "Date"], na_position="last").copy()
        for _, row in df.iterrows():
            home = row["home_team"]
            away = row["away_team"]
            if not home or not away:
                continue

            rh = self._get(home)
            ra = self._get(away)
            k = _k_factor(row.get("Round", ""))

            e_home = _expected_score(rh + ELO_HOME_ADVANTAGE, ra)
            e_away = 1 - e_home
            s_home, s_away = _actual_score(
                row.get("home_score", 0),
                row.get("away_score", 0),
                row.get("Notes", ""),
            )

            self.ratings[home] = rh + k * (s_home - e_home)
            self.ratings[away] = ra + k * (s_away - e_away)

            self.history.append({
                "Year": row.get("Year"),
                "home_team": home,
                "away_team": away,
                "home_elo_before": rh,
                "away_elo_before": ra,
                "home_elo_after": self.ratings[home],
                "away_elo_after": self.ratings[away],
            })

        return self

    def get_all_ratings(self):
        return pd.DataFrame([
            {"team": t, "elo": r}
            for t, r in sorted(self.ratings.items(), key=lambda x: -x[1])
        ])

    def get_2026_ratings(self):
        """User-facing ratings — 2026 teams only."""
        all_ratings = self.get_all_ratings()
        teams_2026 = restrict_team_list(all_ratings["team"])
        return (
            all_ratings[all_ratings["team"].isin(teams_2026)]
            .reset_index(drop=True)
            .assign(rank=lambda d: range(1, len(d) + 1))
        )

    def predict_match(self, home, away):
        rh = self._get(home)
        ra = self._get(away)
        p_home = _expected_score(rh + ELO_HOME_ADVANTAGE, ra)
        p_away = 1 - p_home
        p_draw = 0.0  # knockout tournament — no draws in Elo update for KO after ET
        return {
            "home_team": home,
            "away_team": away,
            "home_elo": rh,
            "away_elo": ra,
            "home_win_prob": p_home,
            "away_win_prob": p_away,
            "elo_diff": rh - ra,
        }

    def win_probability(self, team_a, team_b):
        return _expected_score(self._get(team_a), self._get(team_b))
