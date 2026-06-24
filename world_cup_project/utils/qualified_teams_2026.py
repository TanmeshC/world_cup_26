"""
2026 World Cup qualified teams — the ONLY teams allowed in user-facing outputs.

Source of truth: schedule_2026.csv (48 teams for the expanded 2026 format).
Historical teams not in this list may appear in training data only.
"""

import os
import pandas as pd

from utils.config import SCHEDULE_2026_PATH
from utils.team_standardizer import standardize_team_name

_QUALIFIED_CACHE = None


def _load_from_schedule():
  """Derive qualified teams from the 2026 match schedule."""
  if not os.path.exists(SCHEDULE_2026_PATH):
    return []
  schedule = pd.read_csv(SCHEDULE_2026_PATH)
  teams = set()
  for col in ("home_team", "away_team"):
    if col in schedule.columns:
      teams.update(schedule[col].dropna().apply(standardize_team_name))
  return sorted(t for t in teams if t)


def get_qualified_teams():
  """Return sorted list of 2026 World Cup participants."""
  global _QUALIFIED_CACHE
  if _QUALIFIED_CACHE is None:
    _QUALIFIED_CACHE = _load_from_schedule()
  return list(_QUALIFIED_CACHE)


def is_qualified_2026(team):
  return standardize_team_name(team) in get_qualified_teams()


def filter_2026_teams(df, column):
  """Keep only rows where `column` is a 2026-qualified team."""
  qualified = set(get_qualified_teams())
  return df[df[column].apply(lambda t: standardize_team_name(t) in qualified)].copy()


def filter_2026_matchups(df, home_col="home_team", away_col="away_team"):
  """Keep only rows where BOTH teams are 2026-qualified."""
  qualified = set(get_qualified_teams())
  mask = (
    df[home_col].apply(lambda t: standardize_team_name(t) in qualified)
    & df[away_col].apply(lambda t: standardize_team_name(t) in qualified)
  )
  return df[mask].copy()


def restrict_team_list(teams):
  """Filter an arbitrary team iterable to 2026 participants only."""
  qualified = set(get_qualified_teams())
  return sorted(
    standardize_team_name(t)
    for t in teams
    if standardize_team_name(t) in qualified
  )
