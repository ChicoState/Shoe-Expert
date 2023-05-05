import csv
import random
import string
from decimal import Decimal
from aggregate import Url_Paths
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
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

def gen_test_col_data(model, valid: bool):
  isArray = False
  if isinstance(model, ArrayField):
    isArray = True
    model = model.base_field
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
              data.append(choice[0])
          return data
        else:
          if choices is None:
            return ''.join(random.choice(string.ascii_lowercase) for _ in range(max_length))
          else:
            return choices[random.randint(0, len(choices) - 1)][0]
      else:
        if isArray:
          data = []
          for _ in range(random.randint(2, 5)):
            data.append(''.join(random.choice(string.ascii_lowercase) for _ in range(max_length + 1)))
          return data
        else:
          return ''.join(random.choice(string.ascii_lowercase) for _ in range(max_length + 1))
    case models.DecimalField:
      max_digits = model.max_digits
      decimal_places = model.decimal_places
      if valid:
        rng = 10 ** (max_digits - decimal_places) - 1
        if isArray:
          data = []
          for _ in range(random.randint(2, 5)):
            data.append(Decimal(str(round(random.uniform(0, rng), decimal_places))))
          return data
        else:
          return Decimal(str(round(random.uniform(0, rng), decimal_places)))
      else:
        rng = 10 ** max_digits
        if isArray:
          data = []
          for _ in range(random.randint(2, 5)):
            data.append(Decimal(random.uniform(-rng, rng)))
          return data
        else:
          return Decimal(random.uniform(-rng, rng))
    case models.PositiveIntegerField:
      validators = model.validators
      if valid:
        if isArray:
          data = []
          for _ in range(random.randint(2, 5)):
            data.append(random.randint(validators[0].limit_value, validators[1].limit_value))
          return data
        else:
          return random.randint(validators[0].limit_value, validators[1].limit_value)
      else:
        if isArray:
          data = []
          for _ in range(random.randint(2, 5)):
            if bool(random.randint(0, 1)):
              data.append(random.randint(-validators[0].limit_value + 1, validators[0].limit_value - 1))
            else:
              data.append(random.randint(validators[1].limit_value + 1, 2*validators[1].limit_value))
          return data
        else:
          if bool(random.randint(0, 1)):
            return random.randint(-validators[0].limit_value + 1, validators[0].limit_value - 1)
          else:
            return random.randint(validators[1].limit_value + 1, 2*validators[1].limit_value)
    case models.fields.BooleanField:
      # Impossible to validate: https://docs.python.org/3/library/stdtypes.html#truth-value-testing
      return bool(random.randint(0, 1))
    case _:
      raise TypeError(f"{type(model)} not a known, processable, type")

def create_shoe_object(tc: TestCase, url_path: Url_Paths, valid: bool):
  attrs = []
  for col in url_path.get_django_available_columns():
    attrs.append(gen_test_col_data(url_path.get_column_model(col), valid))
  max_length = globals()[url_path.name.capitalize()].shoe_name.field.max_length
  shoe_name = ''.join(random.choice(string.ascii_lowercase) for _ in range(max_length))
  attrs.append(shoe_name)
  obj = globals()[url_path.name.capitalize()](*tuple(attrs))
  if valid:
    try:
      obj.full_clean()
      obj.save()
    except ValidationError as e:
      errors = []
      for key, value in e.message_dict.items():
        errors.append((key, getattr(obj, key), value))
      tc.fail(f"ValidationError raised for valid object: {errors}")
  else:
    with tc.assertRaises(ValidationError):
      obj.full_clean()
      obj.save()

def create_shoe_model_test(url_path: Url_Paths):
  attrs = {
    '__module__': __name__
  }
  attrs[f"test_create_valid_{url_path.name.lower()}_object"] = lambda self : create_shoe_object(self, url_path, True)
  attrs[f"test_create_invalid_{url_path.name.lower()}_object"] = lambda self : create_shoe_object(self, url_path, False)
  globals()[f"{url_path.name.capitalize()}_test"] = type(f"{url_path.name.title()}_Test", (TestCase,), attrs)

for url_path in Url_Paths:
  create_shoe_model_test(url_path)
