import requests
from bs4 import BeautifulSoup
import pandas as pd

# scrape past matches and results
url = "https://hltv.org/results"
html = requests.get(url)
doc = BeautifulSoup(html.content, "lxml")

match_data = []
results = doc.find_all("div", {"class": "result-con"})
df_results = pd.DataFrame(columns=['team1_name', 'team2_name', 'team1_score', 'team2_score', 'event', 'type'])
for i in results:
    tr_tags = i.find_all("tr")
    for tr in tr_tags:
        td_tags = tr.find_all("td")
        for td in td_tags:
            td_data = (td.get_text().strip())
            match_data.append(td_data)
        match_data[1] = match_data[1].split(' - ')
        match_data.insert(3, match_data[1][0])
        match_data.insert(4, match_data[1][1])
        match_data.pop(1)
        new_df = pd.DataFrame([match_data], columns=df_results.columns)
        df_results = pd.concat([df_results, new_df], ignore_index=True)
        match_data = []


