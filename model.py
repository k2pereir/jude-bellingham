import os
import sys
import warnings
import numpy as np
import pandas as pd
import requests
import xgboost as xgb

def load_fixtures():
    return pd.read_csv("data/fixtures.csv")

def load_historical_scores():
    return pd.read_csv("data/historical_scores.csv")

def load_elo_ratings():
    return pd.read_csv("data/current_elo_ratings.csv")

def load_fifa_rankings():
    return pd.read_csv("data/fifa_team_rankings.csv")

def load_betting_odds():
    return pd.read_csv("data/winning_bets.csv")

def load_standings():
    return pd.read_csv("data/group_standings.csv")

# normalize country names
def normalize_tea_name(team):
    aliases = {
        "USA": "United States",
        "US": "United States",
        "South Korea": "Korea Republic",
        "Iran": "IR Iran",
        "Ivory Coast": "Côte d'Ivoire",
        "Turkey": "Türkiye",
        "Cabo Verde": "Cape Verde",
    }
    team = str(team).strip()
    return aliases.get(team, team)

def get_elo(team, elo_data):
    row = elo_data[elo_data["team"] == team]
    if row.empty:
        raise ValueError(f"No elo rating found for {team}")
    return float(row.iloc[0]['elo'])

# fifa rank
def get_fifa_rank(team, fifa_data):
    row = fifa_data[fifa_data["team"] == team]
    if row.empty:
        raise ValueError(f"No FIFA ranking found for {team}")
    return int(row.iloc[0]["fifa_rank"])

# betting odds
def get_betting_probability(team, betting_data):
    row = betting_data[betting_data["team"] == team]
    if row.empty:
        return np.nan
    return float(row.iloc[0]["no_vig_probability"])


def predict(a, b):
    #TODO: predict

    # determine how important each of the following is for the winner: elo, fifa rank, bets, prev games
    # ^ feature weights for each one - determine arbitrarily

    # make functions to get the info you need for each of the ^ features

    # run all those functions to get the data

    # train, val based on that data

    # return winner, loser, winner_goals, loser_goals

    pass

def update_standings(winner, loser, winner_goals, loser_goals):
    """
    when a team wins, we wanna update the group standings so we can update the fixtures and predict who's playing next
    """
    standings = pd.read_csv("data/group_standings.csv")

    if winner_goals != loser_goals:
        standings.loc[standings["team"] == winner, "points"] += 3
        standings.loc[standings["team"] == winner, "wins"] += 1
        standings.loc[standings["team"] == loser, "losses"] += 1
    else:
        standings.loc[standings["team"] == winner, "points"] += 1
        standings.loc[standings["team"] == loser, "points"] += 1
        standings.loc[standings["team"] == winner, "draws"] += 1
        standings.loc[standings["team"] == loser, "draws"] += 1
    standings.loc[standings["team"] == winner, "goals_for"] += winner_goals
    standings.loc[standings["team"] == loser, "goals_against"] += winner_goals
    standings.loc[standings["team"] == loser, "goals_for"] += loser_goals
    standings.loc[standings["team"] == winner, "goals_against"] += loser_goals
    standings.to_csv("data/group_standings.csv", index=False)

def main():
    today = pd.Timestamp.today().normalize()
    fixtures = pd.read_csv("data/fixtures.csv")
    fixtures["date_dt"] = pd.to_datetime(fixtures["date"])
    fixtures = fixtures[fixtures["date_dt"] >= today]
    
    for i, game in fixtures.iterrows():
        team1, team2 = game["teams"].split(" v ")
        winner, loser, winner_goals, loser_goals = predict(team1, team2)
        update_standings(winner, loser, winner_goals, loser_goals)
        print(f"{team1} vs {team2} - Winner: {winner}")

if __name__ == "__main__":
    main()