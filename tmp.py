import aggregate
from aggregate import Url_Paths
from aggregate import ColumnSelector
from aggregate import Gender
from aggregate import ScraperSingleton

def main():
    # ScraperSingleton.scrape() has NO default value for filename
        # must be user-specified
        # can be either a full or relative path
        # must have the `.csv` file extension
    filename = "womens_track.csv"
    # ScraperSingleton.scrape() defaults `url_path` to RUNNING_SHOES
    url_path = Url_Paths.TRACK_SHOES
    # ScraperSingleton.scrape() defaults `columnlist` to None (All Available Columns Included)
        # Url_Paths defines an instance method get_available_columns():
            # This method returns a list of all available columns
            # Using TRACK_SHOES as an example: `Url_Paths.TRACK_SHOES.get_available_columns()`
    # Note: Including a column in the `columnlist` that is NOT available is an exceptional case
    columnlist = [
        ColumnSelector.BRAND,
        ColumnSelector.EVENT,
        ColumnSelector.FEATURE,
        ColumnSelector.FEATURES,
        ColumnSelector.MSRP,
        ColumnSelector.RELEASE_DATE,
        ColumnSelector.SPIKE_SIZE,
        ColumnSelector.SPIKE_TYPE,
        ColumnSelector.SURFACE,
        ColumnSelector.USE,
        ColumnSelector.WEIGHT
    ]
    # ScraperSingleton.scrape() defaults `gender` to Gender.NONE (All Shoes)
    gender = Gender.WOMEN
    # ScraperSingleton.scrape() defaults `pages` to None (All Pages)
    # Note: page range must start at 1
    pages = range(1, 7, 2)
    # ScraperSingleton.scrape() defaults `sleep` to 0.5 seconds (slow w/ many pages)
    sleep = 0
    # ScraperSingleton.scrape() defaults `timeout` to 10 seconds
    timeout = 1
    try:
        scraper = ScraperSingleton()
        scraper.scrape(
            filename=filename,
            columnlist=columnlist,
            url_path=url_path,
            gender=gender,
            pages=pages,
            sleep=sleep,
            timeout=timeout
        )
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
