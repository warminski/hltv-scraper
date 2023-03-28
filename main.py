from PlayerScraper import PlayerScraper
from ResultsScraper import ResultsScraper


def main():
    results = ResultsScraper()
    print(results.results_df)


if __name__ == "__main__":
    main()
