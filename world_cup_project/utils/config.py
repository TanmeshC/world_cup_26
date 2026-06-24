import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

MATCHES_PATH = os.path.join(DATA_DIR, "matches_1930_2022.csv")
RANKING_PATH = os.path.join(DATA_DIR, "fifa_ranking_2026-06-08.csv")
WORLD_CUP_PATH = os.path.join(DATA_DIR, "world_cup.csv")
SCHEDULE_2026_PATH = os.path.join(DATA_DIR, "schedule_2026.csv")

# Elo parameters
ELO_INITIAL = 1500
ELO_K_GROUP = 40
ELO_K_KNOCKOUT = 50
ELO_K_FINAL = 60
ELO_HOME_ADVANTAGE = 0  # World Cup matches are neutral-site

# Simulation
MONTE_CARLO_ITERATIONS = 10_000
