import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('2022.csv') # Set to season dataset of interest
reg_season_data = data[data['game_id'] <= 272]
playoff_data = data[data['game_id'] >= 273]

# Create a list of playoff game IDs
playoff_game_ids = data[data['game_id'] >= 273]['game_id'].unique()

# Get a list of unique playoff teams (both home and away)
playoff_teams = pd.concat([data[data['game_id'].isin(playoff_game_ids)]['home_team'],
                         data[data['game_id'].isin(playoff_game_ids)]['away_team']]).unique()


# Regular season point differential
team_points = reg_season_data.groupby('home_team')['home_score'].sum() + reg_season_data.groupby('away_team')['away_score'].sum()
opponent_points = reg_season_data.groupby('home_team')['away_score'].sum() + reg_season_data.groupby('away_team')['home_score'].sum()
point_differential = team_points - opponent_points

# Create a DataFrame for plotting
plot_data = pd.DataFrame({'Team': point_differential.index, 'Point Differential': point_differential.values})

# Add a column to indicate playoff teams
plot_data['Playoff Team'] = plot_data['Team'].isin(playoff_teams)

# Barplot
plt.figure(figsize=(12, 6))
sns.barplot(x='Team', y='Point Differential', data=plot_data.sort_values(by='Point Differential', ascending=False),
            hue='Playoff Team', palette=['blue', 'red'], dodge=False)  # Use hue and dodge=False to highlight
plt.xticks(rotation=90)
plt.xlabel("Team")
plt.ylabel("Point Differential")
plt.title("Regular Season Point Differential by Team (Playoff Teams Highlighted)")
plt.tight_layout()
plt.show()


# Playoff point differential
playoff_data['game_point_diff'] = playoff_data['home_score'] - playoff_data['away_score']

# Group by team and sum point differentials (handling home and away games separately)
team_point_diffs_home = playoff_data.groupby('home_team')['game_point_diff'].sum()
team_point_diffs_away = playoff_data.groupby('away_team')['game_point_diff'].apply(lambda x: -x.sum())  # Negate away team differentials

# Combine home and away point differentials, handling missing values
team_point_diffs = team_point_diffs_home.add(team_point_diffs_away, fill_value=0)

# Get all unique teams in the playoffs
playoff_teams = pd.unique(playoff_data[['home_team', 'away_team']].values.ravel())

# Filter team_point_diffs to include only playoff teams
team_point_diffs = team_point_diffs[team_point_diffs.index.isin(playoff_teams)]

# Create a DataFrame for plotting
plot_data = pd.DataFrame({'Team': team_point_diffs.index, 'Point Differential': team_point_diffs.values})

# # Barplot; playoff_point_diff.png
plt.figure(figsize=(12, 6))
sns.barplot(x='Team', y='Point Differential', data=plot_data.sort_values(by='Point Differential', ascending=False))
plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
plt.xlabel("Team")
plt.ylabel("Point Differential")
plt.title("Playoff Point Differential by Team")
plt.tight_layout()
plt.show()
