from aggregate import Url_Paths
from aggregate import ColumnSelector
from aggregate import ScraperSingleton

def main():

    url_path = Url_Paths.SOCCER_CLEATS

    columnlist = [
        ColumnSelector.FEATURES         # For SOCCER_CLEATS only, FEATURES column actually provides Price-Tiers
    ]

    ScraperSingleton().scrape(
        filename="soccer_cleats.csv",
        columnlist=columnlist,
        url_path=url_path,
        pages=range(1, 2),
        sleep=0,
        timeout=1
    )

    return 0


if __name__ == "__main__":
    main()
