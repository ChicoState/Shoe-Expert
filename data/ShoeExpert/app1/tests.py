import csv
from aggregate import Url_Paths
from django.test import TestCase
from django.settings import STATIC_DIR

import importlib
app1_models_module = importlib.import_module('app1.models')
app1_models_module_names = dir(app1_models_module)
app1_models_module_class_names = [name for name in app1_models_module_names if isinstance(getattr(app1_models_module, name), type)]
for name in app1_models_module_class_names:
  globals()[name] = getattr(app1_models_module, name)

# Create your tests here.

def read_csv(filename: str):
  with open(f"{STATIC_DIR}/shoe_data/{filename}.csv", 'r') as f:
    reader = csv.DictReader(f)
    csv_data = [row for row in reader]
  return csv_data

def create_shoe_model_test(url_path: Url_Paths):
  attrs = {
    '__module__': __name__
  }
  attrs[f"test_{url_path.name.lower()}"] = lambda self: self.assertEqual(
    read_csv(url_path.name.title()),
    list(globals()[url_path.name.capitalize()].objects.all().values())
  )
  globals()[f"{url_path.name.captialize()}_test"] = type(f"{url_path.name.title()}_Test", (TestCase,), attrs)

for url_path in Url_Paths:
  create_shoe_model_test(url_path)
