import requests
from bs4 import BeautifulSoup
import pandas as pd

# scrape past matches and results
url = "https://hltv.org/results"
html = requests.get(url)
doc = BeautifulSoup(html.content, "lxml")
results = pd.DataFrame()
tables = doc.find_all("table")
for i in tables:
    team1_name = i.find("div", {"class": "line-align team1"}).get_text().strip()
    team2_name = i.find("div", {"class": "line-align team2"}).get_text().strip()
    team1_score = i.find("td", {"class": "result-score"}).get_text()[0]
    team2_score = i.find("td", {"class": "result-score"}).get_text()[-1]
    event_name = i.find("span", {"class": "event-name"}).get_text()
    formula = i.find("td", {"class": "star-cell"}).get_text().strip()
    # add each match to dataframe
    row = pd.DataFrame(
        [{'team_1': team1_name, 'team_2': team2_name, 'team1_score': team1_score, 'team2_score': team2_score,
          'event_name': event_name, 'formula': formula}])
    results = pd.concat([results, row], ignore_index=True)

print(results.head())
