from aggregate import Url_Paths
from django.db import models

# Create your models here.

def create_shoe_model(url_path: Url_Paths):
    attrs = {
        '__module__': __name__,
        "shoe_name": models.CharField(max_length=128, primary_key=True),
        "__str__": lambda self: self.shoe_name
    }
    for col in url_path.get_django_available_columns():
        attrs[url_path.get_column_name(col, attribute = True)] = url_path.get_column_model(col)
    globals()[url_path.name.capitalize()] = type(url_path.name.title(), (models.Model,), attrs)

for url_path in Url_Paths:
    create_shoe_model(url_path)
