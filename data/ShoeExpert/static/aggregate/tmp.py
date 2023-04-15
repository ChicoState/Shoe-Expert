from aggregate import ColumnSelector, Gender, Url_Paths, ScraperSingleton

def main():
  url_path = Url_Paths.RUNNING_SHOES
  filename = f"/home/docker/data/ShoeExpert/static/shoe_data/{url_path.name.capitalize()}.csv"
  ScraperSingleton().scrape(
    filename = filename,
    url_path=url_path,
    pages=range(1, 5),
    sleep=0.01,
    timeout=1
  )

if __name__ == "__main__":
    main()
