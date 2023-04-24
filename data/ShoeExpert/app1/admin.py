from aggregate import Url_Paths
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.db import models

from import_export import resources
from import_export.fields import Field
from import_export.admin import ImportMixin
from import_export import widgets

import importlib

app1_models_module = importlib.import_module('app1.models')
app1_models_module_names = dir(app1_models_module)
app1_models_module_class_names = [name for name in app1_models_module_names if isinstance(getattr(app1_models_module, name), type)]
for name in app1_models_module_class_names:
    globals()[name] = getattr(app1_models_module, name)

WIDGET_MAPPING = {
    models.BooleanField: widgets.BooleanWidget(),
    models.CharField: widgets.CharWidget(),
    models.DecimalField: widgets.DecimalWidget(),
    models.PositiveIntegerField: widgets.IntegerWidget()
}

def get_widget_for_field(field):
    if isinstance(field, ArrayField):
        field = field.base_field
    if field.__class__ in WIDGET_MAPPING:
        return WIDGET_MAPPING[field.__class__]
    else:
        return None

### Model Resources Below ###

def create_model_resource(url_path):
    attrs = {
        '__module__': __name__,
        "shoe_name": Field(attribute='shoe_name', column_name='SHOE_NAME', widget=widgets.CharWidget()),
        "gender": Field(attribute='gender', column_name='Gender', widget=widgets.CharWidget()),
        'Meta': type('Meta', (object,), {'model': globals()[url_path.name.capitalize()], 'skip_unchanged': True, 'use_transactions': True, 'exclude': ('id'), 'import_id_fields': ('shoe_name',)})
    }
    for col in url_path.get_django_available_columns():
        attr_name = url_path.get_column_name(col, attribute = True)
        display_name = url_path.get_column_name(col)
        attrs[attr_name] = Field(attribute=attr_name, column_name=display_name, widget=get_widget_for_field(url_path.get_column_model(col)))
    resource_name = f"{url_path.name.capitalize()}_resource"
    type_name = f"{url_path.name.title()}_Resource"
    globals()[resource_name] = type(type_name, (resources.ModelResource,), attrs)

### Admin Integration/Mixins Below ###

def create_admin_mixin(url_path):
    attrs = {
        '__module__': __name__,
        "resource_classes": [globals()[f"{url_path.name.capitalize()}_resource"]]
    }
    mixin_name = f"{url_path.name.capitalize()}_admin"
    type_name = f"{url_path.name.title()}_Admin"
    globals()[mixin_name] = type(type_name, (ImportMixin, admin.ModelAdmin), attrs)

### Register Models & Mixins Below ###

def register_model_and_mixin(url_path):
    admin.site.register(globals()[url_path.name.capitalize()], globals()[f"{url_path.name.capitalize()}_admin"])

### RUNNER ###

for url_path in Url_Paths:
    create_model_resource(url_path)
    create_admin_mixin(url_path)
    register_model_and_mixin(url_path)
