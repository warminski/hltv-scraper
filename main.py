import requests
from bs4 import BeautifulSoup
import pandas as pd

# scrape past matches and results



def scrape_one_page(url):
    html = requests.get(url)
    doc = BeautifulSoup(html.content, "lxml")
    results = doc.find_all("div", {"class": "result-con"})
    match_data = []
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
    return df_results


# scrape number of pages
def get_number_of_pages(url):
    html = requests.get(url)
    doc = BeautifulSoup(html.content, "lxml")
    number_of_pages = doc.find("span", {"class": "pagination-data"}).get_text().split()[-1]
    rounded_number_of_pages = (int(number_of_pages) // 100) * 100
    return rounded_number_of_pages


pages = get_number_of_pages("https://hltv.org/results")


df = pd.DataFrame(columns=['team1_name', 'team2_name', 'team1_score', 'team2_score', 'event', 'type'])
for i in range(100, pages, 100):
    url = "https://hltv.org/results"
    new_url = url + f"?offset={i}"
    new_df = scrape_one_page(new_url)
    df = pd.concat([df, new_df], ignore_index=True)
    print(f"scraped page number {i}")

print(df)

