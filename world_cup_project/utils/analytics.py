"""Shared analytics pipeline — loads data once, trains models, caches results."""

import functools

from utils.data_loader import DataLoader
from utils.elo_engine import EloEngine
from utils.power_index import PowerIndex
from utils.feature_engineering import FeatureEngineer


@functools.lru_cache(maxsize=1)
def get_analytics():
    loader = DataLoader()
    loader.load_all()
    matches = loader.clean_matches()
    loader.clean_schedule_2026()

    elo = EloEngine().process_matches(matches)
    engineer = FeatureEngineer(matches, elo)
    power = PowerIndex(
        elo.get_2026_ratings(),
        loader.rankings,
        matches,
    ).compute()

    return {
        "matches": matches,
        "rankings": loader.rankings,
        "world_cup": loader.world_cup,
        "schedule_2026": loader.schedule_2026,
        "elo": elo,
        "engineer": engineer,
        "power_rankings": power,
    }
