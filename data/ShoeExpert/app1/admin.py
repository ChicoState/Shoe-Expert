from django.contrib import admin

from app1.models import RunningShoe

from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportMixin

### Model Resources Below ###

class RunningShoeResource(resources.ModelResource):
    shoe_name = Field(attribute='shoe_name', column_name='SHOE_NAME')
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
    use = Field(attribute='use', column_name='USE')
    waterproofing = Field(attribute='waterproofing', column_name='WATERPROOFING')
    weight = Field(attribute='weight', column_name='WEIGHT')
    width = Field(attribute='width', column_name='WIDTH')

    class Meta:
        model = RunningShoe
        skip_unchanged = True
        use_transactions = True
        exclude = ('id')
        import_id_fields = ('shoe_name',)

### Admin Integration/Mixins Below ###

class RunningShoeAdmin(ImportMixin, admin.ModelAdmin):
    resource_classes = [RunningShoeResource]

### Register Models & Mixins Below ###

admin.site.register(RunningShoe, RunningShoeAdmin)
