"""Champion probability estimator via Monte Carlo tournament simulation."""

import numpy as np
import pandas as pd

from utils.config import MONTE_CARLO_ITERATIONS
from utils.qualified_teams_2026 import get_qualified_teams


class ChampionPredictor:
    def __init__(self, elo_engine, n_simulations=MONTE_CARLO_ITERATIONS):
        self.elo = elo_engine
        self.n_simulations = n_simulations
        self.teams = get_qualified_teams()

    def _simulate_match(self, team_a, team_b):
        p = self.elo.win_probability(team_a, team_b)
        return team_a if np.random.random() < p else team_b

    def _simulate_knockout_round(self, teams):
        winners = []
        shuffled = list(teams)
        np.random.shuffle(shuffled)
        for i in range(0, len(shuffled) - 1, 2):
            winners.append(self._simulate_match(shuffled[i], shuffled[i + 1]))
        if len(shuffled) % 2 == 1:
            winners.append(shuffled[-1])
        return winners

    def simulate_tournament(self):
        remaining = list(self.teams)
        while len(remaining) > 1:
            remaining = self._simulate_knockout_round(remaining)
        return remaining[0]

    def run_simulations(self):
        counts = {t: 0 for t in self.teams}
        for _ in range(self.n_simulations):
            champion = self.simulate_tournament()
            counts[champion] += 1

        df = pd.DataFrame([
            {"team": t, "championships": c, "probability": c / self.n_simulations}
            for t, c in counts.items()
        ])
        return df.sort_values("probability", ascending=False).reset_index(drop=True)

    def get_top_contenders(self, n=10):
        return self.run_simulations().head(n)
