from django.contrib import admin

from app1.models import Shoe
from app1.models import RunningShoe

from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportMixin

### Model Resources Below ###

class RunningShoeResource(resources.ModelResource):
    shoe_name = Field(attribute='shoe_name', column_name='SHOE_NAME', primary_key=True)
    arch_type = Field(attribute='arch_type', column_name='ARCH_TYPE')
    brand = Field(attribute='brand', column_name='BRAND')
    cushioning = Field(attribute='cushioning', column_name='CUSHIONING')
    distance = Field(attribute='distance', column_name='DISTANCE')
    features = Field(attribute='features', column_name='FEATURES')
    flexibility = Field(attribute='flexibility', column_name='FLEXIBILITY')
    forefoot_height = Field(attribute='forefoot_height', column_name='FOREFOOT_HEIGHT')
    heel_height = Field(attribute='heel_height', column_name='HEEL_HEIGHT')
    heel_toe_drop = Field(attribute='heel_toe_drop', column_name='HEEL_TOE_DROP')
    msrp = Field(attribute='msrp', column_name='MSRP')
    pronation = Field(attribute='pronation', column_name='PRONATION')
    release_date = Field(attribute='release_date', column_name='RELEASE_DATE')
    strike_pattern = Field(attribute='strike_pattern', column_name='STRIKE_PATTERN')
    technology = Field(attribute='technology', column_name='TECHNOLOGY')
    terrain = Field(attribute='terrain', column_name='TERRAIN')
    toebox = Field(attribute='toebox', column_name='TOEBOX')
    waterproofing = Field(attribute='waterproofing', column_name='WATERPROOFING')
    weight = Field(attribute='weight', column_name='WEIGHT')
    width = Field(attribute='width', column_name='WIDTH')

    class Meta:
        model = RunningShoe
        skip_unchanged = True
        import_id_fields = ('shoe_name')

### Admin Integration/Mixins Below ###

class RunningShoeAdmin(ImportMixin):
    resource_classes = [RunningShoeResource]

### Register Models & Mixins Below ###

admin.site.register(Shoe, RunningShoe, RunningShoeAdmin)

### Create CSV Functions Below ###

# from aggregate import ColumnSelector, Gender, Url_Paths, ScraperSingleton

# def createRunningShoeCSV(gender = Gender.NONE):
#   filename = "/home/docker/data/ShoeExpert/shoe_csvs/"
#   if (gender is Gender.MEN):
#     filename += "running_shoes_men.csv"
#   elif (gender is Gender.WOMEN):
#     filename += "running_shoes_women.csv"
#   else:
#     filename += "running_shoes.csv"
#   ScraperSingleton().scrape(
#     filename = filename,
#     columnlist = [
#       ColumnSelector.ARCH_TYPE,
#       ColumnSelector.BRAND,
#       ColumnSelector.CUSHIONING,
#       ColumnSelector.DISTANCE,
#       ColumnSelector.FEATURES,
#       ColumnSelector.FLEXIBILITY,
#       ColumnSelector.FOREFOOT_HEIGHT,
#       ColumnSelector.HEEL_HEIGHT,
#       ColumnSelector.HEEL_TOE_DROP,
#       ColumnSelector.MSRP,
#       ColumnSelector.PRONATION,
#       ColumnSelector.RELEASE_DATE,
#       ColumnSelector.STRIKE_PATTERN,
#       ColumnSelector.TECHNOLOGY,
#       ColumnSelector.TERRAIN,
#       ColumnSelector.TOEBOX,
#       ColumnSelector.USE,
#       ColumnSelector.WATERPROOFING,
#       ColumnSelector.WEIGHT,
#       ColumnSelector.WIDTH
#     ],
#     gender=gender,
#     url_path=Url_Paths.RUNNING_SHOES,
#     sleep=0,
#     timeout=1
#   )
