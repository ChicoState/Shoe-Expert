from aggregate import ColumnSelector, Gender, Url_Paths, ScraperSingleton

def main():
  for url_path in Url_Paths:
    # FIXME:
    filename = f"/home/mkapral/GitHub/Shoe-Expert/data/ShoeExpert/static/shoe_data/{url_path.name.title()}.csv"
    ScraperSingleton().scrape(
      filename = filename,
      url_path=url_path
    )

if __name__ == "__main__":
    main()
