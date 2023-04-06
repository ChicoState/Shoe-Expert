from aggregate import ColumnSelector, Gender, Url_Paths, ScraperSingleton

def main():
  i = 1
  j = 2
  while i < 41:
    ScraperSingleton().scrape(
      filename = f"running_shoes_{i}.csv",
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
      pages=range(i, j),
      sleep=0,
      timeout=1
    )
    i = j
    j += 1

if __name__ == "__main__":
    main()
