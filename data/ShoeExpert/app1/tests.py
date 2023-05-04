import csv
import random
import string
from aggregate import Url_Paths
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.test import TestCase

import importlib
app1_models_module = importlib.import_module('app1.models')
app1_models_module_names = dir(app1_models_module)
app1_models_module_class_names = [name for name in app1_models_module_names if isinstance(getattr(app1_models_module, name), type)]
for name in app1_models_module_class_names:
  globals()[name] = getattr(app1_models_module, name)

# Create your tests here.

def get_shoe_names(filename: str):
  csv_data = []
  with open(f"{settings.STATIC_DIR}/shoe_data/{filename}.csv", 'r') as f:
    reader = csv.reader(f)
    _ = next(reader)
    for row in reader:
      csv_data.append(row[0])
  return csv_data

def gen_test_data(model, valid: bool):
  isArray = False
  if isinstance(model, ArrayField):
    isArray = True
    model = model.basefield
  match type(model):
    case models.CharField:
      max_length = model.max_length
      choices = list(model.choices) if model.choices is not None else None
      if valid:
        if isArray:
          data = []
          if choices is None:
            for _ in range(random.randint(2, 5)):
              data.append(''.join(random.choice(string.ascii_lowercase) for _ in range(max_length)))
          else:
            for choice in choices:
              data.append(choice[1])
          return data
        else:
          if choices is None:
            return ''.join(random.choice(string.ascii_lowercase) for _ in range(max_length))
          else:
            return choices[random.randint(0, len(choices) - 1)][1]
      else:
        if isArray:
          data = []
          for _ in range(random.randint(2, 5)):
            data.append(''.join(random.choice(string.ascii_lowercase) for _ in range(max_length + 1)))
        else:
          return ''.join(random.choice(string.ascii_lowercase) for _ in range(max_length + 1))
    case models.DecimalField:
      max_digits = model.max_digits
      decimal_places = model.decimal_places
      if valid:
        if isArray:
          data = []
        else:

      else:
        if isArray:
          data = []
        else:

    case models.PositiveIntegerField:
      validators = model.validators
    case _:
      raise TypeError(f"{type(model)} not a known, processable, type")

def create_shoe_model_test(url_path: Url_Paths):
  attrs = {
    '__module__': __name__,
    'fixtures': ['tests.json']
  }
  attrs[f"test_{url_path.name.lower()}"] = lambda self: self.assertEqual(
    read_csv(url_path.name.title()),
    list(globals()[url_path.name.capitalize()].objects.all().values())
  )
  globals()[f"{url_path.name.capitalize()}_test"] = type(f"{url_path.name.title()}_Test", (TestCase,), attrs)

for url_path in Url_Paths:
  create_shoe_model_test(url_path)
