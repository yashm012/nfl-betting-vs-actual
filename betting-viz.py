import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import difflib

data = pd.read_csv('merged-2022.csv')
data['total_score'] = data['home_score'] + data['away_score']
data['over_under_result'] = data['total_score'] - data['over_under']
data['game_result'] = np.where(data['over_under_result'] > 0, 'Over', 'Under')

# Create a list of playoff game IDs
playoff_game_ids = data[data['game_id'] >= 273]['game_id'].unique()

# Get a list of unique playoff teams (both home and away)
playoff_teams = pd.concat([data[data['game_id'].isin(playoff_game_ids)]['home_team'],
                         data[data['game_id'].isin(playoff_game_ids)]['away_team']]).unique()

reg_season_data = data[data['game_id'] <= 272]
playoff_data = data[data['game_id'] >= 273]

# Countplot; reg_season_o/u.png
plt.figure(figsize=(8, 6))
sns.countplot(x='game_result', data=reg_season_data)
plt.title('# of Regular Season Games Over/Under')
plt.xlabel('Game Result')
plt.ylabel('Count')
plt.show()

# Playoff countplot; playoff_o/u.png
plt.figure(figsize=(8, 6))
sns.countplot(x='game_result', data=playoff_data, palette=['red'])
plt.title('# of Playoff Games Over/Under')
plt.xlabel('Game Result')
plt.ylabel('Count')
plt.show()

# Boxplot; o/u_result_distribution.png
plt.figure(figsize=(8, 6))
sns.boxplot(x='game_result', y='over_under_result', data=data,
            hue=data['game_id'].isin(playoff_game_ids).map({True: 'Playoffs', False: 'Regular Season'}),  # Map to strings
            palette=['blue', 'red'])  # Choose colors for regular and playoff games
plt.title('Over/Under Result Distribution')
plt.xlabel('Game Result')
plt.ylabel('Over/Under Result')
plt.legend(title='Game type', loc='upper right')  # Adjust legend location if needed
plt.show()

def determine_favored_team(row):
    """Determines the favored team based on team ID similarity."""
    home_team = row['home_team']
    away_team = row['away_team']
    favorite_id = row['favorite']

    # Calculate similarity scores between favorite ID and team names
    home_similarity = difflib.SequenceMatcher(None, favorite_id, home_team).ratio()
    away_similarity = difflib.SequenceMatcher(None, favorite_id, away_team).ratio()

    # Return the team name with the highest similarity score
    if home_similarity > away_similarity:
        return home_team
    elif away_similarity > home_similarity:
        return away_team
    else:
        # Handle abbreviations
        if favorite_id == "NE":
            favorite_id = "New England"
        elif favorite_id == "SF":
            favorite_id = "San Francisco"
        elif favorite_id == "GB":
            favorite_id = "Green Bay"
        elif favorite_id == "TB":
            favorite_id = "Tampa Bay"
        elif favorite_id == "KC":
            favorite_id = "Kansas City"

# Apply the function to create a new column 'favored_team'
data['favored_team'] = data.apply(determine_favored_team, axis=1)

def determine_coverage(row):
    # Assuming 'spread_favorite' is the column indicating the favorite team's spread.
    if row['favored_team'] == row['home_team']:  # favored team is home team
        if row['home_score'] - row['away_score'] >= abs(row['spread']):  # home team covered
            return 'Covered'
        else:
            return 'Not Covered'
    elif row['favored_team'] == row['away_team']:  # favored team is away team
        if row['away_score'] - row['home_score'] >= abs(row['spread']):  # away team covered
            return 'Covered'
        else:
            return 'Not Covered'
    else:
        return 'Not Covered'  # Tie or unknown favored team - spread not covered

data['covered'] = data.apply(determine_coverage, axis=1)
data['score_diff'] = data[['home_score', 'away_score']].max(axis=1) - data[['home_score', 'away_score']].min(axis=1)

# Update the reg_season_data and playoff_data DataFrames with the new columns
reg_season_data = data[data['game_id'] <= 272]
playoff_data = data[data['game_id'] >= 273]

# Boxplot; score_diff_distribution.png
plt.figure(figsize=(8, 6))
sns.boxplot(x='covered', y='score_diff', data=data,
            hue=data['game_id'].isin(playoff_game_ids).map({True: 'Playoffs', False: 'Regular Season'}),  # Map to strings
            palette=['blue', 'red'])  # Choose colors for regular and playoff games
plt.title('Score Difference Distribution for Covered and Not Covered Games')
plt.xlabel('Coverage')
plt.ylabel('Score Difference')
plt.legend(title='Game type', loc='upper right')  # Adjust legend location if needed
plt.show()

# Countplot; reg_season_vs_spread.png
team_performance = reg_season_data.groupby(['favored_team', 'covered'])['game_id'].count().reset_index()
team_performance = team_performance.rename(columns={'game_id': 'game_count'})

plt.figure(figsize=(12, 6))  # Adjust figure size as needed
sns.barplot(x='favored_team', y='game_count', hue='covered', data=team_performance,
            hue_order=['Covered', 'Not Covered'], palette=['blue', 'gold'])  # Specify hue_order
plt.title('Team Performance Against the Spread When Favored')
plt.xlabel('Team')
plt.ylabel('Number of Games')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
plt.legend(title='Covered Spread')
plt.tight_layout()
plt.show()

# Countplot; playoff_vs_spread.png
team_performance = playoff_data.groupby(['favored_team', 'covered'])['game_id'].count().reset_index()
team_performance = team_performance.rename(columns={'game_id': 'game_count'})

plt.figure(figsize=(12, 6))  # Adjust figure size as needed
sns.barplot(x='favored_team', y='game_count', hue='covered', data=team_performance,
            hue_order=['Covered', 'Not Covered'], palette=['red', 'gold'])  # Specify hue_order
plt.title('Playoff Team Performance Against the Spread When Favored')
plt.xlabel('Team')
plt.ylabel('Number of Games')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
plt.legend(title='Covered Spread')
plt.tight_layout()
plt.show()
