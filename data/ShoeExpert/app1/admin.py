from aggregate import Url_Paths
from django.contrib import admin

from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportMixin

import importlib

app1_models_module = importlib.import_module('app1.models')
app1_models_module_names = dir(app1_models_module)
app1_models_module_class_names = [name for name in app1_models_module_names if isinstance(getattr(app1_models_module, name), type)]
for name in app1_models_module_class_names:
    globals()[name] = getattr(app1_models_module, name)

### Model Resources Below ###

def create_model_resource(url_path = Url_Paths.RUNNING_SHOES):
    attrs = {
        '__module__': __name__,
        "shoe_name": Field(attribute='shoe_name', column_name='SHOE_NAME'),
        'Meta': type('Meta', (object,), {'model': globals()[url_path.name.capitalize()], 'skip_unchanged': True, 'use_transactions': True, 'exclude': ('id'), 'import_id_fields': ('shoe_name',)}),
    }
    for col in url_path.get_available_columns():
        if col.django_model is not None:
            attrs[col.name.lower()] = Field(attribute=col.name.lower(), column_name=col.name)
    resource_name = url_path.name.capitalize() + '_resource'
    globals()[resource_name] = type(resource_name, (resources.ModelResource,), attrs)

create_model_resource()

# class RunningShoeResource(resources.ModelResource):
#     shoe_name = Field(attribute='shoe_name', column_name='SHOE_NAME')
#     arch_type = Field(attribute='arch_type', column_name='ARCH_TYPE')
#     brand = Field(attribute='brand', column_name='BRAND')
#     cushioning = Field(attribute='cushioning', column_name='CUSHIONING')
#     distance = Field(attribute='distance', column_name='DISTANCE')
#     features = Field(attribute='features', column_name='FEATURES')
#     flexibility = Field(attribute='flexibility', column_name='FLEXIBILITY')
#     forefoot_height = Field(attribute='forefoot_height', column_name='FOREFOOT_HEIGHT')
#     heel_height = Field(attribute='heel_height', column_name='HEEL_HEIGHT')
#     heel_toe_drop = Field(attribute='heel_toe_drop', column_name='HEEL_TOE_DROP')
#     msrp = Field(attribute='msrp', column_name='MSRP')
#     pronation = Field(attribute='pronation', column_name='PRONATION')
#     release_date = Field(attribute='release_date', column_name='RELEASE_DATE')
#     strike_pattern = Field(attribute='strike_pattern', column_name='STRIKE_PATTERN')
#     technology = Field(attribute='technology', column_name='TECHNOLOGY')
#     terrain = Field(attribute='terrain', column_name='TERRAIN')
#     toebox = Field(attribute='toebox', column_name='TOEBOX')
#     use = Field(attribute='use', column_name='USE')
#     waterproofing = Field(attribute='waterproofing', column_name='WATERPROOFING')
#     weight = Field(attribute='weight', column_name='WEIGHT')
#     width = Field(attribute='width', column_name='WIDTH')

#     class Meta:
#         model = RunningShoe
#         skip_unchanged = True
#         use_transactions = True
#         exclude = ('id')
#         import_id_fields = ('shoe_name',)

### Admin Integration/Mixins Below ###

def create_admin_mixin(url_path = Url_Paths.RUNNING_SHOES):
    attrs = {
        '__module__': __name__,
        "resource_classes": [globals()[url_path.name.capitalize() + '_resource']],
    }
    mixin_name = url_path.name.capitalize() + '_admin'
    globals()[mixin_name] = type(mixin_name, (ImportMixin, admin.ModelAdmin), attrs)

create_admin_mixin()

# class RunningShoeAdmin(ImportMixin, admin.ModelAdmin):
#     resource_classes = [RunningShoeResource]

### Register Models & Mixins Below ###

def register_model_and_mixin(url_path = Url_Paths.RUNNING_SHOES):
    admin.site.register(globals()[url_path.name.capitalize()], globals()[url_path.name.capitalize() + '_admin'])

register_model_and_mixin()

# admin.site.register(RunningShoe, RunningShoeAdmin)
