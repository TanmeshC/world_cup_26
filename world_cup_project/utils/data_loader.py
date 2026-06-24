import pandas as pd

from utils.config import (
    MATCHES_PATH,
    RANKING_PATH,
    WORLD_CUP_PATH,
    SCHEDULE_2026_PATH,
)
from utils.team_standardizer import standardize_dataframe_teams


class DataLoader:
    def __init__(self):
        self.matches = None
        self.rankings = None
        self.world_cup = None
        self.schedule_2026 = None

    def load_matches(self):
        self.matches = pd.read_csv(MATCHES_PATH)
        return self.matches

    def load_rankings(self):
        self.rankings = pd.read_csv(RANKING_PATH)
        return self.rankings

    def load_world_cups(self):
        self.world_cup = pd.read_csv(WORLD_CUP_PATH)
        return self.world_cup

    def load_schedule_2026(self):
        self.schedule_2026 = pd.read_csv(SCHEDULE_2026_PATH)
        return self.schedule_2026

    def load_all(self):
        self.load_matches()
        self.load_rankings()
        self.load_world_cups()
        self.load_schedule_2026()
        return self.matches, self.rankings, self.world_cup

    def clean_matches(self):
        df = self.matches.copy()
        df.drop_duplicates(inplace=True)
        df.columns = [c.strip() for c in df.columns]
        df = standardize_dataframe_teams(df, ["home_team", "away_team"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
        self.matches = df
        return df

    def clean_schedule_2026(self):
        df = self.schedule_2026.copy()
        df = standardize_dataframe_teams(df, ["home_team", "away_team"])
        self.schedule_2026 = df
        return df
