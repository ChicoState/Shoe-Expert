from django.contrib import admin

# Register your models here.
from app1.models import Shoe
admin.site.register(Shoe)

### Create CSV Functions Below ####

from aggregate import ColumnSelector, Gender, Url_Paths, ScraperSingleton

def createRunningShoeCSV(gender = Gender.NONE):
  filename = "/home/docker/data/ShoeExpert/shoe_csvs/"
  if (gender is Gender.MEN):
    filename += "running_shoes_men.csv"
  elif (gender is Gender.WOMEN):
    filename += "running_shoes_women.csv"
  else:
    filename += "running_shoes.csv"
  ScraperSingleton().scrape(
    filename = filename,
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
    gender=gender,
    url_path=Url_Paths.RUNNING_SHOES,
    sleep=0,
    timeout=1
  )
