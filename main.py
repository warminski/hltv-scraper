import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.url = "https://www.hltv.org/stats/players?startDate=all"
        self.player_info_df = pd.DataFrame(columns=['nickname', 'name', 'second_name', 'age', 'team'])

    def get_page_content(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'lxml')
        return soup

    def get_player_url(self):
        driver = webdriver.Chrome()
        driver.get(self.url)
        driver.maximize_window()
        # accept cookies
        cookies_dialog = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "CybotCookiebotDialog"))
        )
        accept_button = cookies_dialog.find_element(By.CSS_SELECTOR, "#CybotCookiebotDialogBodyButtonDecline")
        accept_button.click()
        # get page source
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, "html.parser")
        stats_table = soup.find('table', {'class': 'stats-table player-ratings-table'})
        player_col = stats_table.find_all('td', {'class': 'playerCol'})
        for player in player_col:
            player_url = player.find("a", href=True)
            player_url = player_url['href']
            print(player_url)
        return

    # def scrape_player_info(self):
    #     # page = requests.get("https://www.hltv.org/stats/players/11893/zywoo?startDate=all")
    #     # soup = BeautifulSoup(page.content, 'html.parser')
    #     # print(soup)
    #     session = HTMLSession()
    #     r = session.get("https://www.hltv.org/stats/players/11893/zywoo?startDate=all")
    #     r.html.render(sleep=5)
    #     soup = BeautifulSoup(r.html.raw_html, "html.parser")
    #     print(soup)
    #
    #     return
