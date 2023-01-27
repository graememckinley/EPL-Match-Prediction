import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import html5lib
import lxml

# Scrape multiple teams and years
years = list(range(2023, 2017, -1))

# Will contain match logs for one team in one season
all_matches = []

# Define the url we're starting on
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

for year in years:

    # Download HTML
    data = requests.get(standings_url)

    # Initialize BeautifulSoup object
    soup = BeautifulSoup(data.text, features="html.parser")

    # Select the standings table
    standings_table = soup.select('table.stats_table')[0]

    # Find all the <a> tags and get the href property of each link
    links = [link.get("href") for link in standings_table.find_all('a')]

    # Get only the squad links
    links = [link for link in links if '/squads' in link]

    # Adds to the beginning of each link
    # We need the absolute links
    team_urls = [f"https://fbref.com{link}" for link in links]

    # Grab URL for previous seasons
    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com/{previous_season}"

    for team_url in team_urls:

        # Fix all the team names
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        print(team_name, year)

        # Get the HTML from the team URL
        data = requests.get(team_url)

        # Get all the scores and fixtures
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0]

        # Get the shooting stats
        # Same methods as before
        soup = BeautifulSoup(data.text, features="html.parser")
        links = [link.get("href") for link in soup.find_all('a')]
        links = [link for link in links if link and 'all_comps/shooting/' in link]
        data = requests.get(f"https://fbref.com{links[0]}")

        # Read in the shooting stats and format
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()

        # Merge matches and shooting stats
        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
        except ValueError:
            continue

        # Get only Premier League games
        team_data = team_data[team_data["Comp"] == "Premier League"]
        team_data["Season"] = year
        team_data["Team"] = team_name

        # Add the team data to the list of dataframes
        all_matches.append(team_data)

        # Make sure we're not scraping too quickly
        time.sleep(3)


# Combine everything into one dataframe
match_df = pd.concat(all_matches)
match_df.columns = [column.lower() for column in match_df.columns]

# Write to csv
match_df.to_csv("matches.csv")
