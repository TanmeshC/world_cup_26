"""Monte Carlo tournament simulator for 2026 World Cup."""

import numpy as np
import pandas as pd

from utils.config import MONTE_CARLO_ITERATIONS
from utils.qualified_teams_2026 import get_qualified_teams
from models.champion_predictor import ChampionPredictor


class TournamentSimulator(ChampionPredictor):
    """Extends champion predictor with stage-by-stage and upset tracking."""

    def simulate_with_stages(self):
        stages = {}
        remaining = list(self.teams)
        stage_num = 1
        while len(remaining) > 1:
            stage_name = f"Round of {len(remaining)}"
            winners = []
            upsets = []
            shuffled = list(remaining)
            np.random.shuffle(shuffled)
            for i in range(0, len(shuffled) - 1, 2):
                a, b = shuffled[i], shuffled[i + 1]
                p_a = self.elo.win_probability(a, b)
                winner = a if np.random.random() < p_a else b
                winners.append(winner)
                underdog = b if a == winner else a
                fav_prob = max(p_a, 1 - p_a)
                if fav_prob > 0.6 and winner == underdog:
                    upsets.append({"favorite": a if p_a > 0.5 else b, "underdog": winner})
            stages[stage_name] = {"teams": list(remaining), "winners": winners, "upsets": upsets}
            remaining = winners
            stage_num += 1
        return {"champion": remaining[0], "stages": stages}

    def upset_frequency(self, n_sims=1000):
        upset_counts = {}
        for _ in range(n_sims):
            result = self.simulate_with_stages()
            for stage_data in result["stages"].values():
                for u in stage_data["upsets"]:
                    key = u["underdog"]
                    upset_counts[key] = upset_counts.get(key, 0) + 1
        df = pd.DataFrame([
            {"team": t, "upset_wins": c, "rate": c / n_sims}
            for t, c in sorted(upset_counts.items(), key=lambda x: -x[1])
        ])
        qualified = set(get_qualified_teams())
        return df[df["team"].isin(qualified)].reset_index(drop=True)
