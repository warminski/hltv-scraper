import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import undetected_chromedriver as uc
from tqdm import tqdm

import time
from requests_html import HTMLSession


class ResultsScraper:
    def __init__(self):
        self.url = "https://hltv.org/results"
        self.results_df = pd.DataFrame(columns=['team_1', 'team_2', 'score_1', 'score_2', 'event', 'match_type'])

    def scrape_results_page(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        results_list = soup.find_all('div', {'class': 'result-con'})
        results = []
        for result in results_list:
            match_data = []
            rows = result.find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                for col in columns:
                    data = col.get_text().strip()
                    match_data.append(data)
                score = match_data[1].split(' - ')
                match_data.insert(3, score[0])
                match_data.insert(4, score[1])
                match_data.pop(1)
                results.append(match_data)
                match_data = []
        self.results_df = pd.DataFrame(results, columns=self.results_df.columns)
        return self.results_df

    def get_num_pages(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'lxml')
        num_pages = soup.find('span', {'class': 'pagination-data'}).get_text().split()[-1]
        rounded_num_pages = (int(num_pages) // 100) * 100
        return rounded_num_pages

    def scrape_all_results_pages(self):
        first_page_results = self.scrape_results_page()
        results = pd.concat([self.results_df, first_page_results], ignore_index=True)
        pages = self.get_num_pages()
        for i in range(100, pages, 100):
            self.url = self.url + f'?offset={i}'
            next_page_results = self.scrape_results_page()
            results = pd.concat([results, next_page_results], ignore_index=True)
            print(f"scraped page number {i}")
        results.to_json('results.json', indent=4)
        return results


class PlayerScraper:
    def __init__(self):
        self.all_players_table_url = "https://www.hltv.org/stats/players?startDate=all"
        self.player_url = "https://www.hltv.org/"
        self.all_players_stats_df = pd.DataFrame(
            columns=['nickname', 'team', 'rating 2.0', 'DPR', 'KAST_percentage', 'IMPACT', 'ADR', 'KPR', 'Total_kills',
                     'Headshot_percentage', 'Total_deaths', 'K/D_Ratio', 'Damage_round', 'Grenade_dmg_round',
                     'Maps_played', 'Rounds_played', 'Kills_round', 'Assists_round', 'Deaths_round',
                     'Saved_by_teammate_round', 'Saved_teammates_round'])
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = uc.Chrome(options)

    def get_list_of_players_url(self):
        list_of_urls = []
        #self.driver.implicitly_wait(2)
        self.driver.get(self.all_players_table_url)
        content = self.driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, "html.parser")
        stats_table = soup.find('table', {'class': 'stats-table player-ratings-table'})
        player_col = stats_table.find_all('td', {'class': 'playerCol'})
        for player in player_col:
            player_url = player.find("a", href=True)
            player_url = player_url['href']
            list_of_urls.append(player_url)
        return list_of_urls

    def scrape_player_info(self, soup):
        # list for storing all the data
        player_info = []
        # find basic stat box on single player page and scrape data
        summary_box = soup.find('div', {'class': 'summaryBreakdownContainer'})
        name = summary_box.find('h1').get_text()
        player_info.append(name)
        team = summary_box.find('div', {'class': 'SummaryTeamname text-ellipsis'}).get_text()
        player_info.append(team)
        basic_stats = summary_box.find_all('div', {'class': 'summaryStatBreakdownDataValue'})
        for stat in basic_stats:
            player_info.append(stat.get_text())

        # find full stats and scrape it
        stats = soup.find('div', {'class': 'statistics'})
        full_stats = stats.find_all('div', {'class': 'stats-row'})
        for stat in full_stats:
            player_info.append(stat.find_all("span")[1].get_text())
        player_info[4] = round((float(player_info[4].strip('%')) / 100), 3)
        player_info[9] = round((float(player_info[9].strip('%')) / 100), 3)
        for i in range(2, len(player_info)):
            player_info[i] = round(float(player_info[i]), 2)
        player_info.pop()

        # convert data to Dataframe
        player_info_df = pd.DataFrame([player_info], columns=self.all_players_stats_df.columns)

        return player_info_df

    def scrape_all_players(self):
        # get list of all urls
        print("Scraping list of all players.....")
        list_of_urls = self.get_list_of_players_url()
        print("Done")
        current = 0
        # iterate over list of urls and scrape single player data
        print("Scraping players data...")
        for player in tqdm(list_of_urls):
            url = self.player_url+player
            self.driver.get(url)
            content = self.driver.page_source.encode('utf-8').strip()
            soup = BeautifulSoup(content, "html.parser")
            self.all_players_stats_df = pd.concat([self.all_players_stats_df, self.scrape_player_info(soup)], ignore_index=True)
            #print(f"Scraping player {current} of {len(list_of_urls)}")
            current = current+1
        self.driver.quit()
        # save to json
        self.all_players_stats_df.to_json(path_or_buf='players.json')
        return


player_scraper = PlayerScraper()
player_scraper.scrape_all_players()

