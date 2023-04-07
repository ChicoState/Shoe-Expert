from aggregate import ColumnSelector, Gender, Url_Paths, ScraperSingleton

def main():
  ScraperSingleton().scrape(
    filename = f"/dev/shm/running_shoes.csv", # FIXME:
    columnlist = [
      ColumnSelector.ARCH_TYPE,
      ColumnSelector.BRAND,
      ColumnSelector.CUSHIONING,
      ColumnSelector.DISTANCE,
      ColumnSelector.FEATURES,
      ColumnSelector.FLEXIBILITY,
      ColumnSelector.FOREFOOT_HEIGHT,
      ColumnSelector.HEEL_HEIGHT,
      ColumnSelector.HEEL_TOE_DROP,
      ColumnSelector.MSRP,
      ColumnSelector.PRONATION,
      ColumnSelector.RELEASE_DATE,
      ColumnSelector.STRIKE_PATTERN,
      ColumnSelector.TECHNOLOGY,
      ColumnSelector.TERRAIN,
      ColumnSelector.TOEBOX,
      ColumnSelector.USE,
      ColumnSelector.WATERPROOFING,
      ColumnSelector.WEIGHT,
      ColumnSelector.WIDTH
    ],
    url_path=Url_Paths.RUNNING_SHOES,
    pages=range(1, 5),
    sleep=0.01,
    timeout=1
  )

if __name__ == "__main__":
    main()
