import os
import sys
import warnings
import numpy as np
import pandas as pd
import requests
import xgboost as xgb
import matplotlib

def predict(a, b):
    #TODO: predict

    # determine how important each of the following is for the winner: elo, historical scores, fifa rank, bets
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
    standings = pd.read_csv("data/standings.csv")
    standings.loc[standings["team"] == winner, "points"] += 1
    standings.loc[standings["team"] == winner, "wins"] += 1
    standings.loc[standings["team"] == loser, "losses"] += 1
    standings.loc[standings["team"] == winner, "goals_for"] += winner_goals
    standings.loc[standings["team"] == loser, "goals_against"] += winner_goals    

    # need to finish this also
    

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