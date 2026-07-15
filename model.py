import os
import sys
import warnings
import numpy as np
import pandas as pd
import requests

def load_fixtures():
    return pd.read_csv("data/fixtures.csv")

def load_historical_scores():
    return pd.read_csv("data/historical_scores.csv")

def load_elo_ratings():
    print("Loading Elo ratings")
    return pd.read_csv("data/current_elo_ratings.csv")

def load_fifa_rankings():
    print("Loading FIFA rankings")
    return pd.read_csv("data/fifa_team_rankings.csv")

def load_betting_odds():
    print("Loading betting odds")
    return pd.read_csv("data/winning_bets.csv")

def load_standings():
    return pd.read_csv("data/group_standings.csv")

# normalize country names
def normalize_team_name(team):
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
    return float(row.iloc[0]['rating'])

# fifa rank
def get_fifa_rank(team, fifa_data):
    row = fifa_data[fifa_data["team"] == team]
    if row.empty:
        raise ValueError(f"No FIFA ranking found for {team}")
    return int(row.iloc[0]["fifa_rank"])

# betting odds
def get_betting_probability(team, betting_data):
    team = normalize_team_name(team)

    rows = betting_data[
        betting_data["team"].apply(normalize_team_name) == team
    ]

    if rows.empty:
        return 0.5

    probability = rows.iloc[0]["no_vig_probability"]

    if pd.isna(probability):
        return 0.5

    probability = float(probability)

    # Handle percentages such as 14.5 instead of 0.145.
    if probability > 1:
        probability = probability / 100

    return probability


def predict(team1, team2):
    #TODO: predict

    # determine how important each of the following is for the winner: elo, fifa rank, bets, prev games
    # ^ feature weights for each one - determine arbitrarily

    # make functions to get the info you need for each of the ^ features

    # run all those functions to get the data

    # train, val based on that data

    # return winner, loser, winner_goals, loser_goals

    team1 = normalize_team_name(team1)
    team2 = normalize_team_name(team2)

    elo_data = load_elo_ratings()
    fifa_data = load_fifa_rankings()
    betting_data = load_betting_odds()

    elo1 = get_elo(team1, elo_data)
    elo2 = get_elo(team2, elo_data)

    rank1 = get_fifa_rank(team1, fifa_data)
    rank2 = get_fifa_rank(team2, fifa_data)

    bet1 = get_betting_probability(team1, betting_data)
    bet2 = get_betting_probability(team2, betting_data)

    # Elo expected result.
    elo_score1 = 1 / (
        1 + 10 ** ((elo2 - elo1) / 400)
    )

    elo_score2 = 1 - elo_score1

    # convert FIFA rank to a strength score (rank 1 is strongest)
    maximum_rank = max(
        fifa_data["fifa_rank"].max(),
        210,
    )

    rank_score1 = 1 - (
        (rank1 - 1) / (maximum_rank - 1)
    )

    rank_score2 = 1 - (
        (rank2 - 1) / (maximum_rank - 1)
    )

    # combining the three indicators (arbitrariliy chosen)
    strength1 = (
        0.50 * elo_score1
        + 0.25 * rank_score1
        + 0.25 * bet1
    )

    strength2 = (
        0.50 * elo_score2
        + 0.25 * rank_score2
        + 0.25 * bet2
    )

    total_strength = strength1 + strength2

    if total_strength <= 0:
        strength1 = 0.5
        strength2 = 0.5
        total_strength = 1.0

    # assume approximately 2.6 expected total goals (again arbitrary)
    expected_goals1 = (
        2.6 * strength1 / total_strength
    )

    expected_goals2 = (
        2.6 * strength2 / total_strength
    )

    simulations = 10_000

    score_counts = {}

    for _ in range(simulations):
        goals1 = int(
            np.random.poisson(expected_goals1)
        )

        goals2 = int(
            np.random.poisson(expected_goals2)
        )

        score = (goals1, goals2)

        score_counts[score] = (
            score_counts.get(score, 0) + 1
        )

    # select the score that appeared most often
    goals1, goals2 = max(
        score_counts,
        key=score_counts.get,
    )

    if goals1 > goals2:
        return (
            team1,
            team2,
            goals1,
            goals2,
        )

    if goals2 > goals1:
        return (
            team2,
            team1,
            goals2,
            goals1,
        )

    return (
        team1,
        team2,
        goals1,
        goals2,
    )

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
        unresolved_terms = (
            "winner",
            "loser",
            "runner-up",
            "runner up",
            "tbd"
        )
        if (
            team1.lower().startswith(unresolved_terms)
            or team2.lower().startswith(unresolved_terms)
        ):
            print(f"Skipping unresolved fixture: {team1} vs {team2}")
            continue
        winner, loser, winner_goals, loser_goals = predict(team1, team2)
        #update_standings(winner, loser, winner_goals, loser_goals)
        print(f"{team1} vs {team2} - Winner: {winner}")

if __name__ == "__main__":
    main()