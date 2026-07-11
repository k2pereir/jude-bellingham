import os
import sys
import warnings
import numpy as np
import pandas as pd
import requests
import xgboost as xgb
import matplotlib
from pathlib import Path
from typing import Any
from datetime import date 

DATA_DIR = Path("data")
MODEL_PATH = Path("models/world_cup_model.joblib")

# data loading

def load_data() -> dict[str, pd.DataFrame]:
    """Load all project datasets."""

    files = {
        "historical": "fifa_historical_scores.csv",
        "fifa": "fifa_team_rankings.csv",
        "elo": "current_elo_ratings.csv",
        "fixtures": "fixtures.csv",
        "players": "player_stats.csv",
        "squads": "squad_info.csv",
        "bets": "winning_bets.csv",
    }

    data: dict[str, pd.DataFrame] = {}

    for key, filename in files.items():
        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

        data[key] = pd.read_csv(path)

    return data

def normalize_team_name(name: str) -> str:
    aliases = {
        "USA": "United States",
        "US": "United States",
        "South Korea": "Korea Republic",
        "Korea": "Korea Republic",
        "Iran": "IR Iran",
        "Ivory Coast": "Côte d'Ivoire",
        "Czech Republic": "Czechia",
        "Turkey": "Türkiye",
        "DRC": "DR Congo",
        "Congo DR" : "DR Congo",
        "Cabo Verde" : "Cape Verde"
    }

    cleaned = str(name).strip()
    return aliases.get(cleaned, cleaned)


def predict(a, b):
    # loop through todays date up till the end of the world cup
    # predict all match results
    # return winner, loser, winner goals, and loser goals
    #TODO: predict
    pass

def main():
    today = date.today()
    fixtures = pd.read_csv("data/fixtures.csv")


