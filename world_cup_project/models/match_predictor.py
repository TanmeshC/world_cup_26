"""Match outcome predictor trained on historical WC data, predicts 2026 matchups."""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

from utils.qualified_teams_2026 import get_qualified_teams

FEATURE_COLS = [
    "elo_diff",
    "home_elo",
    "away_elo",
    "home_win_rate",
    "away_win_rate",
    "home_goal_diff",
    "away_goal_diff",
]


class MatchPredictor:
    def __init__(self, feature_df):
        self.feature_df = feature_df
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
        )
        self._trained = False
        self.cv_accuracy = None

    def train(self):
        df = self.feature_df.dropna(subset=FEATURE_COLS + ["home_won"])
        X = df[FEATURE_COLS]
        y = df["home_won"]
        self.model.fit(X, y)
        self._trained = True
        scores = cross_val_score(self.model, X, y, cv=5, scoring="accuracy")
        self.cv_accuracy = scores.mean()
        return self

    def predict_match(self, home, away, elo_engine, engineer):
        stats = engineer.build_team_statistics().set_index("team")
        h_elo = elo_engine._get(home)
        a_elo = elo_engine._get(away)
        h_stats = stats.loc[home] if home in stats.index else None
        a_stats = stats.loc[away] if away in stats.index else None

        features = pd.DataFrame([{
            "elo_diff": h_elo - a_elo,
            "home_elo": h_elo,
            "away_elo": a_elo,
            "home_win_rate": h_stats["win_rate"] if h_stats is not None else 0.5,
            "away_win_rate": a_stats["win_rate"] if a_stats is not None else 0.5,
            "home_goal_diff": h_stats["goal_diff"] if h_stats is not None else 0,
            "away_goal_diff": a_stats["goal_diff"] if a_stats is not None else 0,
        }])

        home_prob = self.model.predict_proba(features[FEATURE_COLS])[0][1]
        return {
            "home_team": home,
            "away_team": away,
            "home_win_prob": round(home_prob, 3),
            "away_win_prob": round(1 - home_prob, 3),
            "predicted_winner": home if home_prob >= 0.5 else away,
            "confidence": round(max(home_prob, 1 - home_prob), 3),
        }

    def get_feature_importance(self):
        if not self._trained:
            return pd.DataFrame()
        return pd.DataFrame({
            "feature": FEATURE_COLS,
            "importance": self.model.feature_importances_,
        }).sort_values("importance", ascending=False)
