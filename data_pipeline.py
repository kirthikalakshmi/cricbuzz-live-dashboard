import requests
import pandas as pd
import sqlite3

# API setup
url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

headers = {
    "X-RapidAPI-Key": "e2aa8e4679mshb9a08e6c8507573p129044jsn44ade09a666f ",
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
}

response = requests.get(url, headers=headers)
data = response.json()

teams = []
venues = []
matches = []

for match_type in data['typeMatches']:
    for series in match_type['seriesMatches']:
        if 'seriesAdWrapper' in series:
            for match in series['seriesAdWrapper']['matches']:
                
                info = match['matchInfo']
                
                team1 = info.get('team1', {})
                team2 = info.get('team2', {})
                venue = info.get('venueInfo', {})
                
                # Teams table
                teams.append({"team_id": team1.get("teamId"), "team_name": team1.get("teamName")})
                teams.append({"team_id": team2.get("teamId"), "team_name": team2.get("teamName")})
                
                # Venue table
                venues.append({
                    "venue_id": venue.get("id"),
                    "venue_name": venue.get("ground"),
                    "city": venue.get("city")
                })
                
                # Matches table
                matches.append({
                    "match_id": info.get("matchId"),
                    "team1_id": team1.get("teamId"),
                    "team2_id": team2.get("teamId"),
                    "venue_id": venue.get("id"),
                    "status": info.get("status")
                })

# Convert to DataFrames
teams_df = pd.DataFrame(teams).drop_duplicates()
venues_df = pd.DataFrame(venues).drop_duplicates()
matches_df = pd.DataFrame(matches).drop_duplicates()

# Store in SQL
conn = sqlite3.connect("cricket.db")

teams_df.to_sql("teams", conn, if_exists="replace", index=False)
venues_df.to_sql("venues", conn, if_exists="replace", index=False)
matches_df.to_sql("matches", conn, if_exists="replace", index=False)

print("Tables created successfully!")
