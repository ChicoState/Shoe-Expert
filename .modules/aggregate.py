import atexit
import csv
from datetime import date
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from enum import Enum, EnumMeta
import itertools
import os
import platform
import re
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import sys
import tempfile
import time

class ColumnSelectorEnumMeta(EnumMeta):
    def __new__(metacls, cls, bases, classdict):
        enum_class = super().__new__(metacls, cls, bases, classdict)
        for _, member in enum_class.__members__.items():
            value, modaldict = member._value_
            member._value_ = value
            member.modaldict = modaldict
        return enum_class

class ColumnSelector(Enum, metaclass=ColumnSelectorEnumMeta):
    ARCH_SUPPORT = ("fact-arch-support", { 'has_modal': False })
    ARCH_TYPE = ("fact-arch-type", {
        'has_modal': True,
        'modal_body': 'Height of Arch'
    })
    BRAND = ("fact-brand", { 'has_modal': False })
    CLEAT_DESIGN = ("fact-cleat-design", { 'has_modal': False })
    CLOSURE = ("fact-closure", { 'has_modal': False })
    COLLABORATION = ("fact-collaboration", { 'has_modal': False })
    COLLECTION = ("fact-collection", { 'has_modal': False })
    CONDITION = ("fact-condition", { 'has_modal': False })
    CONSTRUCTION = ("fact-construction", { 'has_modal': False })
    CUSHIONING = ("fact-cushioning", {
        'has_modal': True,
        'modal_body': "Plush means the shoe is meant to feel soft when running. Balanced means the shoe is more responsive and provides greater energy return."
    })
    CUT = ("fact-cut", { 'has_modal': False })
    DESIGNED_BY = ("fact-designed-by", { 'has_modal': False })
    DISTANCE = ("fact-distance", { 'has_modal': False })
    DOWNTURN = ("fact-downturn", { 'has_modal': False })
    EMBELLISHMENT = ("fact-embellishment", { 'has_modal': False })
    ENVIRONMENT = ("fact-environment", { 'has_modal': False })
    EVENT = ("fact-event", { 'has_modal': False })
    EXPERT_RATING = ("fact-expert_score", { 'has_modal': False })
    FEATURE = ("fact-feature", { 'has_modal': False })
    FEATURES = ("fact-features", { 'has_modal': False })
    FIT = ("fact-fit", { 'has_modal': False })
    FOOT_CONDITION = ("fact-foot-condition", { 'has_modal': False })
    FOREFOOT_HEIGHT = ("fact-forefoot-height", { 'has_modal': False })
    FLEXIBILITY = ("fact-flexibility", {
        'has_modal': True,
        'modal_body': "Ability of the sole to bend and flex. A more flexible shoe will allow the foot to move more naturally. A more rigid shoe will provide more support and stability."
    })
    GRAM_INSULATION = ("fact-gram-insulation", { 'has_modal': False })
    HEEL_HEIGHT = ("fact-heel-height", { 'has_modal': False })
    HEEL_TOE_DROP = ("fact-heel-to-toe-drop", {
        'has_modal': True,
        'modal_body': "The difference in height between the heel and the forefoot. A higher heel-to-toe drop will provide more stability and support. A lower heel-to-toe drop will provide more flexibility and a more natural feel."
    })
    INSPIRED_FROM = ("fact-inspired-from", { 'has_modal': False })
    LACE_TYPE = ("fact-lace-type", { 'has_modal': False })
    LACING_SYSTEM = ("fact-lacing-system", { 'has_modal': False })
    LAST_SHAPE = ("fact-last-shape", { 'has_modal': False })
    LEVEL = ("fact-level", { 'has_modal': False })
    LINING = ("fact-lining", { 'has_modal': False })
    LOCKDOWN = ("fact-lockdown", { 'has_modal': False })
    MSRP = ("fact-msrp_formatted", { 'has_modal': False })
    MATERIAL = ("fact-material", { 'has_modal': False })
    MIDSOLE = ("fact-midsole", { 'has_modal': False })
    NUMBER_OF_REVIEWS = ("fact-number-of-reviews", { 'has_modal': False })
    ORIGIN = ("fact-origin", { 'has_modal': False })
    ORTHOTIC_FRIENDLY = ("fact-orthotic-friendly", { 'has_modal': False })
    OUTSOLE = ("fact-outsole", { 'has_modal': False })
    PACE = ("fact-pace", { 'has_modal': False })
    PRINT = ("fact-print", { 'has_modal': False })
    PRONATION = ("fact-pronation", { 'has_modal': False })
    PROTECTION = ("fact-protection", { 'has_modal': False })
    RANDING = ("fact-randing", { 'has_modal': False })
    RELEASE_DATE = ("fact-release-date", { 'has_modal': False })
    REVIEW_TYPE = ("fact-review-type", { 'has_modal': False })
    RIGIDITY = ("fact-rigidity", { 'has_modal': False })
    SALES_PRICE = ("fact-price", { 'has_modal': False })
    SCORE = ("fact-score", { 'has_modal': False })
    SEASON = ("fact-season", { 'has_modal': False })
    SENSITIVITY = ("fact-sensitivity", { 'has_modal': False })
    SHOE_TYPE = ("fact-shoe-type", { 'has_modal': False })
    SIGNATURE = ("fact-signature", { 'has_modal': False })
    SPIKE_SIZE = ("fact-spike-size", { 'has_modal': False })
    SPIKE_TYPE = ("fact-spike-type", { 'has_modal': False })
    STIFFNESS = ("fact-stiffness", { 'has_modal': False })
    STRETCH = ("fact-stretch", { 'has_modal': False })
    STRIKE_PATTERN = ("fact-strike-pattern", {
        'has_modal': True,
        'modal_body': "Strike pattern describes the where the foot hits the ground during a run. Different shoes provide different support for different kinds of strike patterns"
    })
    STUD_TYPE = ("fact-stud-type", { 'has_modal': False })
    STYLE = ("fact-style", { 'has_modal': False })
    SUMMER = ("fact-summer", { 'has_modal': False })
    SURFACE = ("fact-surface", { 'has_modal': False })
    SUPPORT = ("fact-support", { 'has_modal': False })
    TERRAIN = ("fact-terrain", { 'has_modal': False })
    TECHNOLOGY = ("fact-technology", { 'has_modal': False })
    THICKNESS = ("fact-thickness", { 'has_modal': False })
    TOEBOX = ("fact-toebox", { 'has_modal': False })
    TONGUE_PULL_LOOP = ("fact-tongue-pull-loop", { 'has_modal': False })
    TOP = ("fact-top", { 'has_modal': False })
    TYPE = ("fact-type", { 'has_modal': False })
    ULTRA_RUNNING = ("fact-ultra-running", { 'has_modal': False })
    USE = ("fact-use", { 'has_modal': False })
    USER_RATING = ("fact-users_score", { 'has_modal': False })
    WATERPROOFING = ("fact-waterproofing", { 'has_modal': False })
    WEIGHT = ("fact-weight", { 'has_modal': False })
    WIDTH = ("fact-width", { 'has_modal': False })
    WORN_BY = ("fact-worn-by", { 'has_modal': False })
    ZERO_DROP = ("fact-zero-drop", { 'has_modal': False })

    def get_menu_selector(self):
        return (By.CSS_SELECTOR, f"input[type='checkbox'][id='{self.value}'] + span.checkbox")

    def get_data_selector(self):
        if self == ColumnSelector.SCORE:
            return (By.CSS_SELECTOR, "div.catalog-list-slim__facts__column div.catalog-list-slim__shoes-fact__values.corescore__values div.corescore div.corescore__score.score_green")
        else:
            return (By.CSS_SELECTOR, "div.catalog-list-slim__facts__column div.catalog-list-slim__shoes-fact__values span")

    def has_modal(self):
        return self.modaldict['has_modal']

    def get_modal_body(self):
        if self.has_modal():
            return self.modaldict['modal_body']
        else:
            return None

class Gender(Enum):
    MEN = ()
    NONE = ()
    WOMEN = ()

class Url_PathsEnumMeta(EnumMeta):
    def __new__(metacls, cls, bases, classdict):
        enum_class = super().__new__(metacls, cls, bases, classdict)
        for _, member in enum_class.__members__.items():
            value, filterdict = member._value_
            member._value_ = value
            member.filterdict = filterdict
        return enum_class

class Url_Paths(Enum, metaclass=Url_PathsEnumMeta):
    APPROACH_SHOES = (
        "approach-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('tongue pull loop', "Tongue Pull Loop"), ('expensive', "Expensive"), ('cheap', "Cheap"), ('lightweight', "Lightweight"), ('heel brake', "Heel Brake"), ('breathable', "Breathable"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Tongue Pull Loop' if re.search(r'tongue\s*pull\s*loop', s.lower()) else None, 'Expensive' if 'expensive' in s.lower() else None, 'Cheap' if 'cheap' in s.lower() else None, 'Lightweight' if 'lightweight' in s.lower() else None, 'Heel Brake' if re.search(r'heel\s*brake', s.lower()) else None, 'Breathable' if 'breathable' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PROTECTION: {
                "name": "Protection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RANDING: {
                "name": "Randing",
                "units": None,
                "django_model": models.CharField(max_length=10, choices=(('full', "Full"), ('forefoot', "Forefoot")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Full' if 'full' in s.lower() else 'Forefoot' if 'forefoot' in s.lower() else None
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SENSITIVITY: {
                "name": "Sensitivity",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SUPPORT: {
                "name": "Support",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOP: {
                "name": "Top",
                "units": None,
                "django_model": models.CharField(max_length=4, choices=(('low', "Low"), ('mid', "Mid")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Low' if 'low' in s.lower() else 'Mid' if 'mid' in s.lower() else None
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WATERPROOFING: {
                "name": "Waterproofing",
                "units": None,
                "django_model": models.CharField(max_length=32, choices=(('waterproof', "Waterproof"), ('water resistant', "Water Resistant")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Waterproof' if 'waterproof' in s.lower() else 'Water Resistant' if re.search(r'water\s*resistant', s.lower()) else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    BASKETBALL_SHOES = (
        "basketball-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('expensive', "Expensive"), ('retro', "Retro"), ('ankle support', "Ankle Support"), ('outdoor', "Outdoor"), ('cheap', "Cheap"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Expensive' if 'expensive' in s.lower() else None, 'Retro' if 'retro' in s.lower() else None, 'Ankle Support' if re.search(r'ankle\s*support', s.lower()) else None, 'Outdoor' if 'outdoor' in s.lower() else None, 'Cheap' if 'cheap' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.LOCKDOWN: {
                "name": "Lockdown",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('fitadapt', "FitAdapt"), ('zipper', "Zipper"), ('laces', "Laces"), ('strap', "Strap"), ('slip-on', "Slip-On"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['FitAdapt' if 'fitadapt' in s.lower() else None, 'Zipper' if 'zipper' in s.lower() else None, 'Laces' if 'lace-up' in s.lower() else None, 'Strap' if 'strap' in s.lower() else None, 'Slip-On' if 'slip-on' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SIGNATURE: {
                "name": "Signature",
                "units": None,
                "django_model": models.CharField(max_length=128, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOP: {
                "name": "Top",
                "units": None,
                "django_model": models.CharField(max_length=5, choices=(('low', "Low"), ('mid', "Mid"), ('high', "High")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Low' if 'low' in s.lower() else 'Mid' if 'mid' in s.lower() else 'High' if 'high' in s.lower() else None
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    CLIMBING_SHOES = (
        "climbing-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('laces', "Laces"), ('velcro', "Velcro"), ('slip-on', "Slip-On"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Laces' if 'lace' in s.lower() else None, 'Velcro' if 'velcro' in s.lower() else None, 'Slip-On' if 'slip-on' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CONSTRUCTION: {
                "name": "Construction",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('no-edge', "No-Edge"), ('board lasted', "Board Lasted"), ('slip lasted', "Slip Lasted"), ('vegan', "Vegan"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['No-Edge' if 'no-edge' in s.lower() else None, 'Board Lasted' if re.search(r'board\s*lasted', s.lower()) else None, 'Slip Lasted' if re.search(r'slip\s*lasted', s.lower()) else None, 'Vegan' if 'vegan' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.DOWNTURN: {
                "name": "Downturn",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('neutral', "Neutral"), ('moderate', "Moderate"), ('aggressive', "Aggressive")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Neutral' if 'neutral' in s.lower() else 'Moderate' if 'moderate' in s.lower() else 'Aggressive' if 'aggressive' in s.lower() else None
            },
            ColumnSelector.ENVIRONMENT: {
                "name": "Environment",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('indoor', "Indoor"), ('outdoor', "Outdoor"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Indoor' if 'indoor' in s.lower() else None, 'Outdoor' if 'outdoor' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('expensive', "Expensive"), ('split tongue', "Split Tongue"), ('lightweight', "Lightweight"), ('cheap', "Cheap"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Expensive' if 'expensive' in s.lower() else None, 'Split Tongue' if re.search('split tongue', s.lower()) else None, 'Lightweight' if 'lightweight' in s.lower() else None, 'Cheap' if 'cheap' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.FIT: {
                "name": "Fit",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('performance', "Performance"), ('comfort', "Comfort")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Performance' if 'performance' in s.lower() else 'Comfort' if 'comfort' in s.lower() else None
            },
            ColumnSelector.LAST_SHAPE: {
                "name": "Last Shape",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('asymmetric', "Asymmetric"), ('straight', "Straight")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Asymmetric' if 'asymmetric' in s.lower() else 'Straight' if 'straight' in s.lower() else None
            },
            ColumnSelector.LEVEL: {
                "name": "Level",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('beginner', "Beginner"), ('intermediate', "Intermediate"), ('advanced', "Advanced"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Beginner' if 'beginner' in s.lower() else None, 'Intermediate' if 'intermediate' in s.lower() else None, 'Advanced' if 'advanced' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.LINING: {
                "name": "Lined",
                "units": None,
                "django_model": models.BooleanField(blank=True, null=True),
                "lambda_serializer": lambda s: True if re.search(r'\blined\b', s.lower()) else False if re.search(r'\bunlined\b', s.lower()) else None
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MIDSOLE: {
                "name": "Midsole",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('yes', "Yes"), ('full', "Full"), ('partial', "Partial"), ('no', "No")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Yes' if re.search(r'with\s*midsole', s.lower()) else 'Full' if 'full' in s.lower() else 'Partial' if 'partial' in s.lower() else 'No' if re.search(r'without\s*midsole', s.lower()) else None
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.STIFFNESS: {
                "name": "Stiffness",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('soft', "Soft"), ('medium', "Medium"), ('stiff', "Stiff")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Soft' if 'soft' in s.lower() else 'Medium' if 'medium' in s.lower() else 'Stiff' if '3/3' in s.lower() else None
            },
            ColumnSelector.STRETCH: {
                "name": "Stretch",
                "units": None,
                "django_model": models.BooleanField(blank=True, null=True),
                "lambda_serializer": lambda s: True if re.search(r'size\s*stretch', s.lower()) else False if re.search(r'no\s*stretch', s.lower()) else None
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.THICKNESS: {
                "name": "Thickness",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.TONGUE_PULL_LOOP: {
                "name": "Tongue Pull Loop",
                "units": None,
                "django_model": models.BooleanField(blank=True, null=True),
                "lambda_serializer": lambda s: True if 'true' in s.lower() else False if 'n/a' in s.lower() or 'false' in s.lower() else None
            },
            ColumnSelector.TOP: {
                "name": "Top",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('low', "Low"), ('mid', "Mid")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Low' if 'low' in s.lower() else 'Mid' if 'mid' in s.lower() else None
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('trad', "Trad"), ('face', "Face"), ('slab', "Slab"), ('overhang', "Overhang"), ('crack', "Crack"), ('sport', "Sport"), ('bouldering', "Bouldering"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Trad' if 'trad' in s.lower() or 'all' in s.lower() else None, 'Face' if 'face' in s.lower() or 'all' in s.lower() else None, 'Slab' if 'slab' in s.lower() or 'all' in s.lower() else None, 'Overhang' if 'overhang' in s.lower() or 'all' in s.lower() else None, 'Crack' if 'crack' in s.lower() or 'all' in s.lower() else None, 'Sport' if 'sport' in s.lower() or 'all' in s.lower() else None, 'Bouldering' if 'bouldering' in s.lower() or 'all' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WORN_BY: {
                "name": "Worn By",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            }
        }
    )
    CROSSFIT_SHOES = (
        "crossfit-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FOREFOOT_HEIGHT: {
                "name": "Forefoot Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_HEIGHT: {
                "name": "Heel Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "name": "Heel to Toe Drop",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOEBOX: {
                "name": "Toebox",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('narrow', "Narrow"), ('medium', "Medium"), ('wide', "Wide"), ('extra wide', "Extra Wide")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Narrow' if 'narrow' in s.lower() else 'Wide' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(extra\s*)?(wide)', s.lower())) else 'Extra Wide' if re.search(r'extra\s*wide', s.lower()) else 'Medium' if 'medium' in s.lower() else None
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "name": "Widths Available",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(("narrow", "Narrow"), ("standard", "Standard"), ("wide", "Wide"), ("extra wide", "Extra Wide"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Narrow' if 'narrow' in s.lower() else None, 'Standard' if 'normal' in s.lower() else None, 'Wide' if re.search(r'(?<!\-)wide', s.lower()) else None, 'Extra Wide' if 'x-wide' in s.lower() else None])).rstrip(', ') + '}'
            }
        }
    )
    CYCLING_SHOES = (
        "cycling-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLEAT_DESIGN: {
                "name": "Cleat Design",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=8, choices=(('flat', "Flat"), ('2 holes', "2 Holes"), ('3 holes', "3 Holes"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Flat' if 'flat' in s.lower() else None, '2 Holes' if re.search(r'2\s*holes', s.lower()) else None, '3 Holes' if re.search(r'3\s*holes', s.lower()) else None])).rstrip(', ') + '}'
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=8, choices=(('velcro', "Velcro"), ('speed', "Speed"), ('ratchet', "Ratchet"), ('lace', "Lace"), ('BOA', "BOA"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Velcro' if 'velcro' in s.lower() else None, 'speed' if 'Speed' in s.lower() else None, 'Ratchet' if 'ratchet' in s.lower() else None, 'BOA' if 'boa' in s.lower() else None, 'Lace' if 'lace' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURE: {
                "name": "Feature",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RIGIDITY: {
                "name": "Rigidity",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('rigid', "Rigid"), ('stiff', "Stiff"), ('moderate', "Moderate"), ('flexible', "Flexible")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Rigid' if '4/4' in s.lower() else 'Stiff' if '3/4' in s.lower() else 'Moderate' if '2/4' in s.lower() else 'Flexible' if '1/4' in s.lower() else None
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('winter', "Winter"), ('indoor', "Indoor"), ('cyclocross', "Cyclocross"), ('casual', "Casual"), ('triathlon', "Triathlon"), ('gravel', "Gravel"), ('mountain', "Mountain"), ('road', "Road"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Winter' if 'winter' in s.lower() else None, 'Indoor' if 'indoor' in s.lower() else None, 'Cyclocross' if 'cyclocross' in s.lower() else None, 'Casual' if 'casual' in s.lower() else None, 'Triathlon' if 'triathlon' in s.lower() else None, 'Gravel' if 'gravel' in s.lower() else None, 'Mountain' if 'mountain' in s.lower() else None, 'Road' if 'road' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    FOOTBALL_CLEATS = (
        "football-cleats",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('strap', "Strap"), ('laces', "Laces"), ('ghost lacing', "Ghost Lacing"), ('slip-on', "Slip-On"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Strap' if 'strap' in s.lower() else None, 'Laces' if 'lace' in s.lower() else None, 'Ghost Lacing' if re.search(r'ghost\s*lacing', s.lower()) else None, 'Slip-On' if 'slip-on' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Price Tier",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('cheap', "Cheap"), ('expensive', "Expensive")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Cheap' if 'cheap' in s.lower() else 'Expensive' if 'expensive' in s.lower() else None
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.STUD_TYPE: {
                "name": "Molded Studs",
                "units": None,
                "django_model": models.BooleanField(blank=True, null=True),
                "lambda_serializer": lambda s: True if 'molded' in s.lower() else None
            },
            ColumnSelector.TOP: {
                "name": "Top",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('high', "High"), ('mid', "Mid"), ('low', "Low")), blank=True, null=True),
                "lambda_serializer": lambda s: 'High' if 'high' in s.lower() else 'Mid' if 'mid' in s.lower() else 'Low' if 'low' in s.lower() else None
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "name": "Width",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('narrow', "Narrow"), ('medium', "Medium"), ('wide', "Wide")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Narrow' if 'narrow' in s.lower() else 'Medium' if 'medium' in s.lower() else 'Wide' if 'wide' in s.lower() else None
            }
        }
    )
    GOLF_SHOES = (
        "golf-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('laces', "Laces"), ('slip-on', "Slip-On"), ('BOA', "BOA"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Laces' if 'laces' in s.lower() else None, 'Slip-On' if 'slip-on' in s.lower() else None, 'BOA' if 'boa' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('cheap', "Cheap"), ('breathable', "Breathable"), ('expensive', "Expensive"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Cheap' if 'cheap' in s.lower() else None, 'Breathable' if 'breathable' in s.lower() else None, 'Expensive' if 'expensive' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('leather', "Leather"), ('synthetic', "Synthetic"), ('knit', "Knit"), ('ortholite', "Ortholite"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Leather' if 'leather' in s.lower() else None, 'Synthetic' if 'synthetic' in s.lower() else None, 'Knit' if 'knit' in s.lower() else None, 'Ortholite' if 'ortholite' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.OUTSOLE: {
                "name": "Spiked",
                "units": None,
                "django_model": models.BooleanField(blank=True, null=True),
                "lambda_serializer": lambda s: True if 'spiked' in s.lower() else False if 'spike-less' in s.lower() else None
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.STYLE: {
                "name": "Style",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('athletic', "Athletic"), ('traditional', "Traditional")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Athletic' if 'athletic' in s.lower() else 'Traditional' if 'traditional' in s.lower() else None
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WATERPROOFING: {
                "name": "Waterproofing",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('waterproof', "Waterproof"), ('water-resistant', "Water-Resistant"), ('water-repellant', "Water-Repellant")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Waterproof' if 'waterproof' in s.lower() else 'Water-Resistant' if 'water-resistant' in s.lower() else 'Water-Repellant' if 'water-repellant' in s.lower() else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    HIKING_BOOTS = (
        "hiking-boots",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CONSTRUCTION: {
                "name": "Construction",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CUT: {
                "name": "Cut",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('mid', "Mid"), ('high', "High")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Mid' if 'mid' in s.lower() else 'High' if 'high' in s.lower() else None
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FIT: {
                "name": "Fit",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('narrow heel', "Narrow Heel"), ('wide toebox', "Wide Toebox"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Narrow Heel' if 'narrow' in s.lower() else None, 'Wide Toebox' if 'wide' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.FOOT_CONDITION: {
                "name": "Foot Condition",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.GRAM_INSULATION: {
                "name": "Gram Insulation",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ORIGIN: {
                "name": "Origin",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('USA', "USA"), ('European', "European"), ('Italian', "Italian"), ('German', "German"), ('Asian', "Asian")), blank=True, null=True),
                "lambda_serializer": lambda s: 'USA' if 'usa' in s.lower() else 'European' if 'european' in s.lower() else 'Italian' if 'italian' in s.lower() else 'German' if 'german' in s.lower() else 'Asian' if 'asian' in s.lower() else None
            },
            ColumnSelector.ORTHOTIC_FRIENDLY: {
                "name": "Orthotic Friendly",
                "units": None,
                "django_model": models.BooleanField(blank=True, null=True),
                "lambda_serializer": lambda s: True if 'true' in s.lower() else False if 'n/a' in s.lower() or 'false' in s.lower() else None
            },
            ColumnSelector.PRONATION: {
                "name": "Pronation",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PROTECTION: {
                "name": "Protection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SEASON: {
                "name": "Season",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=8, choices=(('winter', "Winter"), ('summer', "Summer"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Winter' if 'winter' in s.lower() else None, 'Summer' if 'summer' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.SUPPORT: {
                "name": "Support",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('day', "Day"), ('backpacking', "Backpacking"), ('urban', "Urban"), ('light', "Light"), ('alpine', "Alpine"), ('snow', "Snow"), ('water', "Water"), ('speed', "Speed"), ('desert', "Desert"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Day' if 'day' in s.lower() else None, 'Backpacking' if 'backpacking' in s.lower() else None, 'Urban' if 'urban' in s.lower() else None, 'Light' if 'light' in s.lower() else None, 'Alpine' if 'alpine' in s.lower() else None, 'Snow' if 'snow' in s.lower() else None, 'Water' if 'water' in s.lower() else None, 'Speed' if 'speed' in s.lower() else None, 'Desert' if 'desert' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WATERPROOFING: {
                "name": "Waterproofing",
                "units": None,
                # BUG FOUND HERE DUE TO UNIT TESTING
                "django_model": models.CharField(max_length=16, choices=(('waterproof', "Waterproof"), ('water repellent', 'Water Repellent')), blank=True, null=True),
                "lambda_serializer": lambda s: 'Water Repellent' if 'repellent' in s.lower() else 'Waterproof' if 'waterproof' in s.lower() else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "name": "Widths Available",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(("narrow", "Narrow"), ("standard", "Standard"), ("wide", "Wide"), ("extra wide", "Extra Wide"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Narrow' if 'narrow' in s.lower() else None, 'Standard' if 'normal' in s.lower() else None, 'Wide' if re.search(r'(?<!\-)wide', s.lower()) else None, 'Extra Wide' if 'x-wide' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.ZERO_DROP: {
                "name": "Zero Drop",
                "units": None,
                "django_model": models.BooleanField(blank=True, null=True),
                "lambda_serializer": lambda s: True if 'true' in s.lower() else False if 'false' in s.lower() or 'n/a' in s.lower() else None
            }
        }
    )
    HIKING_SHOES = (
        "hiking-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('laces', "Laces"), ('slip on', "Slip On")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Laces' if 'lace up' in s.lower() else 'Slip On' if 'slip on' in s.lower() else None
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CONSTRUCTION: {
                "name": "Construction",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CUT: {
                "name": "Cut",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('low', "Low"), ('mid', "Mid")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Low' if 'low' in s.lower() else 'Mid' if 'mid' in s.lower() else None
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FIT: {
                "name": "Fit",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FOOT_CONDITION: {
                "name": "Foot Condition",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.GRAM_INSULATION: {
                "name": "Gram Insulation",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ORIGIN: {
                "name": "Origin",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PRONATION: {
                "name": "Pronation",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('supination', 'Supination'), ('underpronation', 'Underpronation'), ('neutral', 'Neutral'), ('overpronation', 'Overpronation'), ('severe overpronation', 'Severe Overpronation'))), blank=True, null=True),
                "lambda_serializer": lambda x: '{' + ', '.join(filter(None, ['Supination' if 'supination' in x.lower() else None, 'Underpronation' if 'underpronation' in x.lower() else None, 'Neutral' if 'neutral' in x.lower() else None, 'Overpronation' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(severe\s*)?(overpronation)', x.lower())) else None, 'Severe Overpronation' if re.search(r'severe\s*overpronation', x.lower()) else None])).rstrip(', ') + '}'
            },
            ColumnSelector.PROTECTION: {
                "name": "Protection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SEASON: {
                "name": "Season",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=10, choices=(('summer', "Summer"), ('winter', "Winter"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Summer' if 'summer' in s.lower() else None, 'Winter' if 'winter' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.SUPPORT: {
                "name": "Support",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('snow', "Snow"), ('desert', "Desert"), ('water', "Water"), ('backpacking', "Backpacking"), ('light', "Light"), ('speed', "Speed"), ('urban', "Urban"), ('day', "Day"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Snow' if 'snow' in s.lower() else None, 'Desert' if 'desert' in s.lower() else None, 'Water' if 'water' in s.lower() else None, 'Backpacking' if 'backpacking' in s.lower() else None, 'Light' if 'light' in s.lower() else None, 'Speed' if 'speed' in s.lower() else None, 'Urban' if 'urban' in s.lower() else None, 'Day' if 'day' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WATERPROOFING: {
                "name": "Waterproofing",
                "units": None,
                "django_model": models.CharField(max_length=32, choices=(('waterproof', "Waterproof"), ('water repellant', "Water Repellant")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Waterproof' if 'waterproof' in s.lower() else 'Water Repellant' if re.search(r'water\s*repellant', s.lower()) else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "name": "Widths Available",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(("narrow", "Narrow"), ("standard", "Standard"), ("wide", "Wide"), ("extra wide", "Extra Wide"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Narrow' if 'narrow' in s.lower() else None, 'Standard' if 'normal' in s.lower() else None, 'Wide' if re.search(r'(?<!\-)wide', s.lower()) else None, 'Extra Wide' if 'x-wide' in s.lower() else None])).rstrip(', ') + '}'
            }
        }
    )
    RUNNING_SHOES = (
        "running-shoes",
        {
            ColumnSelector.ARCH_SUPPORT: {
                "name": "Arch Support",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(("stability", "Stability"), ("neutral", "Neutral"), ("motion control", "Motion control")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Stability' if 'stability' in s.lower() else 'Neutral' if 'neutral' in s.lower() else 'Motion control' if re.search(r'motion\s*control', s.lower()) else None
            },
            ColumnSelector.ARCH_TYPE: {
                "name": "Arch Type",
                "units": None,
                "django_model": models.CharField(max_length=5, choices=(("low", "Low"), ("high", "High")), blank=True, null=True),
                "lambda_serializer": lambda s: 'High' if s == 'High arch' else 'Low' if s == 'Low arch' else None
            },
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CUSHIONING: {
                "name": "Cushioning",
                "units": None,
                "django_model": models.CharField(max_length=10, choices=(('firm', "Firm"), ('balanced', "Balanced"), ('plush', "Plush")), blank=True, null=True),
                "lambda_serializer": lambda s: "Firm" if "firm" in s.lower() else "Balanced" if "balanced" in s.lower() else "Plush" if "plush" in s.lower() else None
            },
            ColumnSelector.DISTANCE: {
                "name": "Distance",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FLEXIBILITY: {
                "name": "Flexibility",
                "units": None,
                "django_model": models.CharField(max_length=24, choices=(('rigid', "Rigid"), ('semi-rigid', "Semi-Rigid"), ('balanced', "Balanced"), ('semi-flexible', "Semi-Flexible"), ('flexible', "Flexible")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Rigid' if 'very stiff' in s.lower() else 'Semi-Rigid' if 'stiff' in s.lower() else 'Balanced' if 'moderate' in s.lower() else 'Semi-Flexible' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(very\s*)?(flexible)', s.lower())) else 'Flexible' if re.search(r'very\s*flexible', s.lower()) else None
            },
            ColumnSelector.FOOT_CONDITION: {
                "name": "Foot Condition",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FOREFOOT_HEIGHT: {
                "name": "Forefoot Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_HEIGHT: {
                "name": "Heel Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "name": "Heel to Toe Drop",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PACE: {
                "name": "Pace",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PRONATION: {
                "name": "Pronation",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('supination', 'Supination'), ('underpronation', 'Underpronation'), ('neutral', 'Neutral'), ('overpronation', 'Overpronation'), ('severe overpronation', 'Severe Overpronation'))), blank=True, null=True),
                "lambda_serializer": lambda x: '{' + ', '.join(filter(None, ['Supination' if 'supination' in x.lower() else None, 'Underpronation' if 'underpronation' in x.lower() else None, 'Neutral' if 'neutral' in x.lower() else None, 'Overpronation' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(severe\s*)?(overpronation)', x.lower())) else None, 'Severe Overpronation' if re.search(r'severe\s*overpronation', x.lower()) else None])).rstrip(', ') + '}'
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SEASON: {
                "name": "Season",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.STRIKE_PATTERN: {
                "name": "Strike Pattern",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=10, choices=(('forefoot', "Forefoot"), ('midfoot', "Midfoot"), ('heel', "Heel"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Forefoot' if 'forefoot' in s.lower() else None, 'Midfoot' if 'midfoot' in s.lower() else None, 'Heel' if 'heel' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.SUMMER: {
                "name": "Summer",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TERRAIN: {
                "name": "Terrain",
                "units": None,
                "django_model": models.CharField(max_length=5, choices=(('road', "Road"), ('trail', "Trail")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Road' if 'road' in s.lower() else 'Trail' if 'trail' in s.lower() else None
            },
            ColumnSelector.TOEBOX: {
                "name": "Toebox",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('narrow', "Narrow"), ('medium', "Medium"), ('wide', "Wide"), ('extra wide', "Extra Wide")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Narrow' if 'narrow' in s.lower() else 'Wide' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(extra\s*)?(wide)', s.lower())) else 'Extra Wide' if re.search(r'extra\s*wide', s.lower()) else 'Medium' if 'medium' in s.lower() else None
            },
            ColumnSelector.TYPE: {
                "name": "Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ULTRA_RUNNING: {
                "name": "Ultra Running",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WATERPROOFING: {
                "name": "Waterproofing",
                "units": None,
                # BUG FOUND HERE DUE TO UNIT TESTING
                "django_model": models.CharField(max_length=16, choices=(('waterproof', "Waterproof"), ('water repellent', 'Water Repellent')), blank=True, null=True),
                "lambda_serializer": lambda s: 'Water Repellent' if 'repellent' in s.lower() else 'Waterproof' if 'waterproof' in s.lower() else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "name": "Widths Available",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(("narrow", "Narrow"), ("standard", "Standard"), ("wide", "Wide"), ("extra wide", "Extra Wide"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Narrow' if 'narrow' in s.lower() else None, 'Standard' if 'normal' in s.lower() else None, 'Wide' if re.search(r'(?<!\-)wide', s.lower()) else None, 'Extra Wide' if 'x-wide' in s.lower() else None])).rstrip(', ') + '}'
            }
        }
    )
    SNEAKERS = (
        "sneakers",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('pull toggle', "Pull Toggle"), ('buckle', "Buckle"), ('zipper', "Zipper"), ('velcro', "Velcro"), ('laces', "Laces"), ('slip-on', "Slip-On"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Pull Toggle' if re.search(r'pull\s*toggle', s.lower()) else None, 'Buckle' if 'buckle' in s.lower() else None, 'Zipper' if 'zipper' in s.lower() else None, 'Velcro' if 'velcro' in s.lower() else None, 'Laces' if 'laces' in s.lower() else None, 'Slip-On' if 'slip-on' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.COLLABORATION: {
                "name": "Collaboration",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.DESIGNED_BY: {
                "name": "Designed By",
                "units": None,
                "django_model": models.CharField(max_length=128, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EMBELLISHMENT: {
                "name": "Embellishment",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('rhinestone', "Rhinestone"), ('sequin', "Sequin"), ('spikes', "Spikes"), ('embroidered', "Embroidered"), ('crystal', "Crystal"), ('glitter', "Glitter")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Rhinestone' if 'rhinestone' in s.lower() else 'Sequin' if 'sequin' in s.lower() else 'Spikes' if 'spikes' in s.lower() else 'Embroidered' if 'embroidered' in s.lower() else 'Crystal' if 'crystal' in s.lower() else 'Glitter' if 'glitter' in s.lower() else None
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.INSPIRED_FROM: {
                "name": "Inspired From",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('running', "Running"), ('casual', "Casual"), ('skate', "Skate"), ('basketball', "Basketball"), ('hiking', "Hiking"), ('tennis', "Tennis"), ('training', "Training"), ('football', "Football"), ('soccer', "Soccer"), ('boat', "Boat")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Running' if 'running' in s.lower() else 'Casual' if 'casual' in s.lower() else 'Skate' if 'skate' in s.lower() else 'Basketball' if 'basketball' in s.lower() else 'Hiking' if 'hiking' in s.lower() else 'Tennis' if 'tennis' in s.lower() else 'Training' if 'training' in s.lower() else 'Football' if 'football' in s.lower() else 'Soccer' if 'soccer' in s.lower() else 'Boat' if 'boat' in s.lower() else None
            },
            ColumnSelector.LACE_TYPE: {
                "name": "Lace Type",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('self-lacing', "Self-Lacing"), ('cotton lace', "Cotton Lace"), ('round lace', "Round Lace"), ('synthetic lace', "Synthetic Lace"), ('no lace', "No Lace"), ('leather lace', "Leather Lace"), ('elastic lace', "Elastic Lace"), ('flat lace', "Flat Lace"), ('toggle lace', "Toggle Lace"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Self-Lacing' if 'self-lacing' in s.lower() else None, 'Cotton Lace' if re.search(r'cotton\s*lace', s.lower()) else None, 'Round Lace' if re.search(r'round\s*lace', s.lower()) else None, 'Synthetic Lace' if re.search(r'synthetic\s*lace', s.lower()) else None, 'No Lace' if re.search(r'no\s*lace', s.lower()) else None, 'Leather Lace' if re.search(r'leather\s*lace', s.lower()) else None, 'Elastic Lace' if re.search(r'elastic\s*lace', s.lower()) else None, 'Flat Lace' if re.search(r'flat\s*lace', s.lower()) else None, 'Toggle Lace' if re.search(r'toggle\s*lace', s.lower()) else None])).rstrip(', ') + '}'
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ORIGIN: {
                "name": "Origin",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('USA', "USA"), ('European', "European"), ('Italian', "Italian"), ('German', "German"), ('Asian', "Asian")), blank=True, null=True),
                "lambda_serializer": lambda s: 'USA' if 'usa' in s.lower() else 'European' if 'european' in s.lower() else 'Italian' if 'italian' in s.lower() else 'German' if 'german' in s.lower() else 'Asian' if 'asian' in s.lower() else None
            },
            ColumnSelector.PRINT: {
                "name": "Print",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('snakeskin', "Snakeskin"), ('leopard', "Leopard"), ('camouflage', "Camouflage"), ('floral', "Floral"), ('tiger', "Tiger"), ('striped', "Striped"), ('rainbow', "Rainbow"), ('tie dye', "Tie Dye"), ('cheetah', "Cheetah"), ('zebra', "Zebra"), ('flame', "Flame"), ('checkered', "Checkered"), ('animal', "Animal"), ('graphic', "Graphic"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Snakeskin' if 'snakeskin' in s.lower() else None, 'Leopard' if 'leopard' in s.lower() else None, 'Camouflage' if 'camouflage' in s.lower() else None, 'Floral' if 'floral' in s.lower() else None, 'Tiger' if 'tiger' in s.lower() else None, 'Striped' if 'striped' in s.lower() else None, 'Rainbow' if 'rainbow' in s.lower() else None, 'Tie Dye' if re.search(r'tie\s*dye', s.lower()) else None, 'Cheetah' if 'cheetah' in s.lower() else None, 'Zebra' if 'zebra' in s.lower() else None, 'Flame' if 'flame' in s.lower() else None, 'Checkered' if 'checkered' in s.lower() else None, 'Animal' if 'animal' in s.lower() else None, 'Graphic' if 'graphic' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SEASON: {
                "name": "Season",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=8, choices=(('spring', "Spring"), ('summer', "Summer"), ('fall', "Fall"), ('winter', "Winter"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Spring' if 'spring' in s.lower() else None, 'Summer' if 'summer' in s.lower() else None, 'Fall' if 'fall' in s.lower() else None, 'Winter' if 'winter' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.STYLE: {
                "name": "Style",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('retro', "Retro"), ('classic', "Classic"), ('Dad', "Dad"), ('sporty', "Sporty"), ('minimalist', "Minimalist"), ('platform', "Platform"), ('sock', "Sock"), ('futuristic', "Futuristic"), ('dressy', "Dressy"), ('chunky', "Chunky"), ('sneakerboots', "Sneakerboots"), ('mule', "Mule"), ('wedge', "Wedge"), ('deconstructed', "Deconstructed"), ('clogs', "Clogs"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Retro' if 'retro' in s.lower() else None, 'Classic' if 'classic' in s.lower() else None, 'Dad' if 'dad' in s.lower() else None, 'Sporty' if 'sporty' in s.lower() else None, 'Minimalist' if 'minimalist' in s.lower() else None, 'Platform' if 'platform' in s.lower() else None, 'Sock' if 'sock' in s.lower() else None, 'Futuristic' if 'futuristic' in s.lower() else None, 'Dressy' if 'dressy' in s.lower() else None, 'Chunky' if 'chunky' in s.lower() else None, 'Sneakerboots' if 'sneakerboots' in s.lower() else None, 'Mule' if 'mule' in s.lower() else None, 'Wedge' if 'wedge' in s.lower() else None, 'Deconstructed' if 'deconstructed' in s.lower() else None, 'Clogs' if 'clogs' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOP: {
                "name": "Top",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('low', "Low"), ('mid', "Mid"), ('high', "High")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Low' if 'low' in s.lower() else 'Mid' if 'mid' in s.lower() else 'High' if 'high' in s.lower() else None
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    SOCCER_CLEATS = (
        "soccer-cleats",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.LACING_SYSTEM: {
                "name": "Lacing System",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('ghost lacing', "Ghost Lacing"), ('laced', "Laced"), ('laceless', "Laceless")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Ghost Lacing' if re.search(r'ghost\s*lacing', s.lower()) else 'Laced' if 'laced' in s.lower() else 'Laceless' if 'laceless' in s.lower() else None
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Price Tier",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('cheap', "Cheap"), ('expensive', "Expensive")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Cheap' if 'cheap' in s.lower() else 'Expensive' if 'expensive' in s.lower() else None
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SIGNATURE: {
                "name": "Signature",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SURFACE: {
                "name": "Surface",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('flexible ground', "Flexible Ground"), ('soft ground', "Soft Ground"), ('indoor', "Indoor"), ('turf', "Turf"), ('firm ground', "Firm Ground"), ('street', "Street")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Flexible Ground' if re.search(r'flexible\s*ground', s.lower()) else 'Soft Ground' if re.search(r'soft\s*ground', s.lower()) else 'Indoor' if 'indoor' in s.lower() else 'Turf' if 'turf' in s.lower() else 'Firm Ground' if re.search(r'firm\s*ground', s.lower()) else 'Street' if 'street' in s.lower() else None
            },
            ColumnSelector.TOP: {
                "name": "Top",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('low', "Low"), ('mid', "Mid"), ('high', "High")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Low' if 'low' in s.lower() else 'Mid' if 'mid' in s.lower() else 'High' if 'high' in s.lower() else None
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    TENNIS_SHOES = (
        "tennis-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLABORATION: {
                "name": "Collaboration",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CONSTRUCTION: {
                "name": "Construction",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('speed', "Speed"), ('stability', "Stability"), ('cushioned', "Cushioned")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Speed' if 'speed' in s.lower() else 'Stability' if 'stability' in s.lower() else 'Cushioned' if 'cushioned' in s.lower() else None
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURE: {
                "name": "Feature",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SHOE_TYPE: {
                "name": "Surface",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=8, choices=(('clay', "Clay"), ('hard', "Hard"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Clay' if 'clay' in s.lower() or 'all' in s.lower() else None, 'Hard' if 'hard' in s.lower() or 'all' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    TRACK_SHOES = (
        "track-and-field-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('slip-on', "Slip-On"), ('hook & loop', "Hook & Loop"), ('lace-up', "Lace-Up"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Slip-On' if 'slip-on' in s.lower() else None, 'Hook & Loop' if re.search(r'hook\s*and\s*loop', s.lower()) else None, 'Lace-Up' if 'lace-up' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EVENT: {
                "name": "Event",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('running', "Running"), ('throwing', "Throwing"), ('jumping', "Jumping")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Running' if 'running' in s.lower() else 'Throwing' if 'throwing' in s.lower() else 'Jumping' if 'jumping' in s.lower() else None
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURE: {
                "name": "Feature",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SPIKE_SIZE: {
                "name": "Spike Size",
                "units": "inch",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.CharField(max_length=8, choices=(('3/8', "3/8"), ('5/16', "5/16"), ('1/4', "1/4"), ('3/16', "3/16"), ('1/8', "1/8")), blank=True, null=True),
                "lambda_serializer": lambda s: '3/8' if '3/8' in s.lower() else '5/16' if '5/16' in s.lower() else '1/4' if '1/4' in s.lower() else '3/16' if '3/16' in s.lower() else '1/8' if '1/8' in s.lower() else None
            },
            ColumnSelector.SPIKE_TYPE: {
                "name": "Spike Type",
                "units": None,
                "django_model": models.CharField(max_length=8, choices=(('pyramid', "Pyrimad"), ('blank', "Blank"), ('tree', "Tree")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Pyramid' if 'pyramid' in s.lower() else 'Blank' if 'blank' in s.lower() else 'Tree' if 'tree' in s.lower() else None
            },
            ColumnSelector.SURFACE: {
                "name": "Surface",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('indoor', "Indoor"), ('asphalt', "Asphalt"), ('grass', "Grass"), ('dirt', "Dirt"), ('wood', "Wood"), ('rubber', "Rubber"), ('all-weather', "All-Weather"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Indoor' if 'indoor' in s.lower() else None, 'Asphalt' if 'asphalt' in s.lower() else None, 'Grass' if 'grass' in s.lower() else None, 'Dirt' if 'dirt' in s.lower() else None, 'Wood' if 'wood' in s.lower() else None, 'Rubber' if 'rubber' in s.lower() else None, 'All-Weather' if 'all-weather' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('shot put', "Shot Put"), ('mid distance', "Mid Distance"), ('sprints', "Sprints"), ('long distance', "Long Distance"), ('high jump', "High Jump"), ('pole vault', "Pole Vault"), ('long jump', "Long Jump"), ('cross country', "Cross Country"), ('triple jump', "Triple Jump"), ('discus', "Discus"), ('hurdles', "Hurdles"), ('hammer throw', "Hammer Throw"), ('javelin', "Javelin"), ('relays', "Relays"), ('steeplechase', "Steeplechase"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Shot Put' if re.search(r'shot\s*put', s.lower()) else None, 'Mid Distance' if re.search(r'mid\s*distance', s.lower()) else None, 'Sprints' if 'sprints' in s.lower() else None, 'Long Distance' if re.search(r'long\s*distance', s.lower()) else None, 'High Jump' if re.search(r'high\s*jump', s.lower()) else None, 'Pole Vault' if re.search(r'pole\s*vault', s.lower()) else None, 'Long Jump' if re.search(r'long\s*jump', s.lower()) else None, 'Cross Country' if re.search(r'cross\s*country', s.lower()) else None, 'Triple Jump' if re.search(r'triple\s*jump', s.lower()) else None, 'Discus' if 'discus' in s.lower() else None, 'Hurdles' if 'hurdles' in s.lower() else None, 'Hammer Throw' if re.search(r'hammer\s*throw', s.lower()) else None, 'Javelin' if 'javelin' in s.lower() else None, 'Relays' if 'relays' in s.lower() else None, 'Steeplechase' if 'steeplechase' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )
    TRAIL_SHOES = (
        "trail-running-shoes",
        {
            ColumnSelector.ARCH_SUPPORT: {
                "name": "Arch Support",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(("stability", "Stability"), ("neutral", "Neutral"), ("motion control", "Motion control")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Stability' if 'stability' in s.lower() else 'Neutral' if 'neutral' in s.lower() else 'Motion control' if re.search(r'motion\s*control', s.lower()) else None
            },
            ColumnSelector.ARCH_TYPE: {
                "name": "Arch Type",
                "units": None,
                "django_model": models.CharField(max_length=5, choices=(("low", "Low"), ("high", "High")), blank=True, null=True),
                "lambda_serializer": lambda s: 'High' if s == 'High arch' else 'Low' if s == 'Low arch' else None
            },
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CUSHIONING: {
                "name": "Cushioning",
                "units": None,
                "django_model": models.CharField(max_length=10, choices=(('firm', "Firm"), ('balanced', "Balanced"), ('plush', "Plush")), blank=True, null=True),
                "lambda_serializer": lambda s: "Firm" if "firm" in s.lower() else "Balanced" if "balanced" in s.lower() else "Plush" if "plush" in s.lower() else None
            },
            ColumnSelector.DISTANCE: {
                "name": "Distance",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FLEXIBILITY: {
                "name": "Flexibility",
                "units": None,
                "django_model": models.CharField(max_length=24, choices=(('rigid', "Rigid"), ('semi-rigid', "Semi-Rigid"), ('balanced', "Balanced"), ('semi-flexible', "Semi-Flexible"), ('flexible', "Flexible")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Rigid' if 'very stiff' in s.lower() else 'Semi-Rigid' if 'stiff' in s.lower() else 'Balanced' if 'moderate' in s.lower() else 'Semi-Flexible' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(very\s*)?(flexible)', s.lower())) else 'Flexible' if re.search(r'very\s*flexible', s.lower()) else None
            },
            ColumnSelector.FOOT_CONDITION: {
                "name": "Foot Condition",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FOREFOOT_HEIGHT: {
                "name": "Forefoot Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_HEIGHT: {
                "name": "Heel Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "name": "Heel to Toe Drop",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PACE: {
                "name": "Pace",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PRONATION: {
                "name": "Pronation",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('supination', 'Supination'), ('underpronation', 'Underpronation'), ('neutral', 'Neutral'), ('overpronation', 'Overpronation'), ('severe overpronation', 'Severe Overpronation'))), blank=True, null=True),
                "lambda_serializer": lambda x: '{' + ', '.join(filter(None, ['Supination' if 'supination' in x.lower() else None, 'Underpronation' if 'underpronation' in x.lower() else None, 'Neutral' if 'neutral' in x.lower() else None, 'Overpronation' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(severe\s*)?(overpronation)', x.lower())) else None, 'Severe Overpronation' if re.search(r'severe\s*overpronation', x.lower()) else None])).rstrip(', ') + '}'
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SEASON: {
                "name": "Season",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.STRIKE_PATTERN: {
                "name": "Strike Pattern",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=10, choices=(('forefoot', "Forefoot"), ('midfoot', "Midfoot"), ('heel', "Heel"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Forefoot' if 'forefoot' in s.lower() else None, 'Midfoot' if 'midfoot' in s.lower() else None, 'Heel' if 'heel' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.SUMMER: {
                "name": "Summer",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "name": "Technology",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TERRAIN: {
                "name": "Terrain",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOEBOX: {
                "name": "Toebox",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('narrow', "Narrow"), ('medium', "Medium"), ('wide', "Wide"), ('extra wide', "Extra Wide")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Narrow' if 'narrow' in s.lower() else 'Wide' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(extra\s*)?(wide)', s.lower())) else 'Extra Wide' if re.search(r'extra\s*wide', s.lower()) else 'Medium' if 'medium' in s.lower() else None
            },
            ColumnSelector.TYPE: {
                "name": "Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ULTRA_RUNNING: {
                "name": "Ultra Running",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WATERPROOFING: {
                "name": "Waterproofing",
                "units": None,
                # BUG FOUND HERE DUE TO UNIT TESTING
                "django_model": models.CharField(max_length=16, choices=(('waterproof', "Waterproof"), ('water repellent', 'Water Repellent')), blank=True, null=True),
                "lambda_serializer": lambda s: 'Water Repellent' if 'repellent' in s.lower() else 'Waterproof' if 'waterproof' in s.lower() else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "name": "Widths Available",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(("narrow", "Narrow"), ("standard", "Standard"), ("wide", "Wide"), ("extra wide", "Extra Wide"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Narrow' if 'narrow' in s.lower() else None, 'Standard' if 'normal' in s.lower() else None, 'Wide' if re.search(r'(?<!\-)wide', s.lower()) else None, 'Extra Wide' if 'x-wide' in s.lower() else None])).rstrip(', ') + '}'
            }
        }
    )
    TRAINING_SHOES = (
        "training-shoes",
        {
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('expensive', "Expensive"), ('high drop', "High Drop"), ('slip-on', "Slip-On"), ('minimalist', "Minimalist"), ('cheap', "Cheap"), ('low drop', "Low Drop"), ('lightweight', "Lightweight"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Expensive' if 'expensive' in s.lower() else None, 'High Drop' if re.search(r'high\s*drop', s.lower()) else None, 'Slip-On' if 'slip-on' in s.lower() else None, 'Minimalist' if 'minimalist' in s.lower() else None, 'Cheap' if 'cheap' in s.lower() else None, 'Low Drop' if re.search(r'low\s*drop', s.lower()) else None, 'Lightweight' if 'lightweight' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.FOREFOOT_HEIGHT: {
                "name": "Forefoot Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_HEIGHT: {
                "name": "Heel Height",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "name": "Heel to Toe Drop",
                "units": "mm",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: (round(sum(map(float, re.sub(r'[^\d.-]', '', re.sub(r'-{2,}', '-', x.strip('-'))).split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOEBOX: {
                "name": "Toebox",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('narrow', "Narrow"), ('medium', "Medium"), ('wide', "Wide"), ('extra wide', "Extra Wide")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Narrow' if 'narrow' in s.lower() else 'Wide' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(extra\s*)?(wide)', s.lower())) else 'Extra Wide' if re.search(r'extra\s*wide', s.lower()) else 'Medium' if 'medium' in s.lower() else None
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "name": "Widths Available",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(("narrow", "Narrow"), ("standard", "Standard"), ("wide", "Wide"), ("extra wide", "Extra Wide"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Narrow' if 'narrow' in s.lower() else None, 'Standard' if 'normal' in s.lower() else None, 'Wide' if re.search(r'(?<!\-)wide', s.lower()) else None, 'Extra Wide' if 'x-wide' in s.lower() else None])).rstrip(', ') + '}'
            }
        }
    )
    WALKING_SHOES = (
        "walking-shoes",
        {
            ColumnSelector.ARCH_SUPPORT: {
                "name": "Arch Support",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(("stability", "Stability"), ("neutral", "Neutral"), ("motion control", "Motion control")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Stability' if 'stability' in s.lower() else 'Neutral' if 'neutral' in s.lower() else 'Motion control' if re.search(r'motion\s*control', s.lower()) else None
            },
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "name": "Closure",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=8, choices=(('bungee', "Bungee"), ('velcro', "Velcro"), ('lace-up', "Lace-Up"), ('slip-on', "Slip-On"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Bungee' if 'bungee' in s.lower() else None, 'Velcro' if 'velcro' in s.lower() else None, 'Lace-Up' if 'lace-up' in s.lower() else None, 'Slip-On' if 'slip-on' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.COLLECTION: {
                "name": "Collection",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CONDITION: {
                "name": "Condition",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EXPERT_RATING: {
                "name": "Expert Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "name": "Features",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('wool', "Wool"), ('suede', "Suede"), ('mesh', "Mesh"), ('knit', "Knit"), ('synthetic', "Synthetic"), ('canvas', "Canvas"), ('leather', "Leather")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Wool' if 'wool' in s.lower() else 'Suede' if 'suede' in s.lower() else 'Mesh' if 'mesh' in s.lower() else 'Knit' if 'knit' in s.lower() else 'Synthetic' if 'synthetic' in s.lower() else 'Canvas' if 'canvas' in s.lower() else 'Leather' if 'leather' in s.lower() else None
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.RELEASE_DATE: {
                "name": "Release Date",
                "units": None,
                "django_model": models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(date.today().year + 1)], blank=True, null=True),
                "lambda_serializer": lambda s: date.today().year if "New" in s else next((int(x) for x in s.split(', ') if x.isdigit() and int(x) > 1970), None)
            },
            ColumnSelector.REVIEW_TYPE: {
                "name": "Review Type",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SALES_PRICE: {
                "name": "Sales Price",
                "units": "USD",
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SCORE: {
                "name": "Score",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SURFACE: {
                "name": "Surface",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('cobblestone', "Cobblestone"), ('trail', "Trail"), ('concrete', "Concrete"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(filter(None, ['Cobblestone' if 'cobblestone' in s.lower() else None, 'Trail' if 'trail' in s.lower() else None, 'Concrete' if 'concrete' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.TOEBOX: {
                "name": "Toebox",
                "units": None,
                "django_model": models.CharField(max_length=16, choices=(('narrow', "Narrow"), ('medium', "Medium"), ('wide', "Wide"), ('extra wide', "Extra Wide")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Narrow' if 'narrow' in s.lower() else 'Wide' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(extra\s*)?(wide)', s.lower())) else 'Extra Wide' if re.search(r'extra\s*wide', s.lower()) else 'Medium' if 'medium' in s.lower() else None
            },
            ColumnSelector.USE: {
                "name": "Use",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USER_RATING: {
                "name": "User Rating",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                # BUG FOUND DUE TO UNIT TESTING
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[MinValueValidator(0)]),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )

    def get_column_name(self, column, attribute = False, display_units = True):
        if isinstance(column, ColumnSelector):
            name = self.filterdict[column]["name"]
            if attribute:
                name = name.lower().replace(' ', '_')
            elif display_units:
                units = self.get_column_units(column)
                if units is not None:
                    name += f" ({units})"
            return name
        else:
            raise TypeError("column must be a ColumnSelector")

    def get_column_units(self, column):
        if isinstance(column, ColumnSelector):
            return self.filterdict[column]["units"]
        else:
            raise TypeError("column must be a ColumnSelector")

    def get_column_model(self, column):
        if isinstance(column, ColumnSelector):
            return self.filterdict[column]["django_model"]
        else:
            raise TypeError("column must be a ColumnSelector")

    def get_column_lambda(self, column):
        if isinstance(column, ColumnSelector):
            return self.filterdict[column]["lambda_serializer"]
        else:
            raise TypeError("column must be a ColumnSelector")

    def get_available_columns(self):
        return list(self.filterdict.keys())

    def get_django_available_columns(self):
        retlist = []
        for column, obj in self.filterdict.items():
            if obj["django_model"] is not None:
                retlist.append(column)
        return retlist

    def get_url_path(self, gender=Gender.NONE):
        prefix = "/catalog/"
        if gender is Gender.NONE:
            return f"{prefix}{self.value}"
        elif gender is Gender.MEN:
            return f"{prefix}mens-{self.value}"
        elif gender is Gender.WOMEN:
            return f"{prefix}womens-{self.value}"
        else:
            raise TypeError("gender must be an enumeration member of Gender")

    def get_default_dict(self):
        avail_list = self.get_available_columns()
        ret = {}
        for column in avail_list:
            if column != ColumnSelector.MSRP:
                ret[column] = True
            else:
                ret[column] = False
        return ret

    def get_truth_dict(self):
        avail_list = self.get_available_columns()
        ret = {}
        for column in avail_list:
            ret[column] = True
        return ret

    def get_false_dict(self):
        avail_list = self.get_available_columns()
        ret = {}
        for column in avail_list:
            ret[column] = False
        return ret

class ScraperSingleton:
    _browser = None
    _chromium_location = "/usr/bin/chromium"    # SHOULD NOT BE MODIFIED
    _column_filter_dict = None
    _domain = "runrepeat.com"                   # SHOULD NOT BE MODIFIED
    _driver_path = "/usr/bin/chromedriver"      # SHOULD NOT BE MODIFIED
    _sleep = 0.01
    _timeout = 1
    _url = f"https://{_domain}"

    @classmethod
    def _cleanup(cls):
        if cls._browser is not None:
            cls._browser.quit()
            cls._browser = None

    @classmethod
    def _resetClassVariables(cls):
        cls._column_filter_dict = None
        cls._sleep = 0.01
        cls._timeout = 1
        cls._url = f"https://{cls._domain}"

    @classmethod
    def _getShoeNames(cls):
        shoe_names = None
        names = cls._browser.find_elements(By.CSS_SELECTOR, "a.catalog-list-slim__names")
        if len(names) > 0:
            if shoe_names is None:
                shoe_names = []
            for name in names:
                shoe_names.append(name.text)
        return shoe_names

    @classmethod
    def _applyColumns(cls):
        cls._scroll_and_click(selector=(By.CSS_SELECTOR, "button.buy_now_button[data-v-795eb1ee]"))

    @classmethod
    def _editColumns(cls):
        cls._scroll_and_click(selector=(By.CSS_SELECTOR, "button.buy_now_button.edit-columns__button"))

    @classmethod
    def _getColumnFilterDict(cls, url_path):
        if cls._column_filter_dict is None:
            cls._column_filter_dict = url_path.get_default_dict()
        return cls._column_filter_dict

    @classmethod
    def _getEmptyView(cls, url_path):
        checkboxes = None
        filter_dict = cls._getColumnFilterDict(url_path=url_path)
        if filter_dict != url_path.get_false_dict():
            for key, value in filter_dict.items():
                if value:
                    if checkboxes is None:
                        checkboxes = []
                    checkboxes.append(key.get_menu_selector())
            if checkboxes is not None:
                cls._editColumns()
                for selector in checkboxes:
                    try:
                        cls._scroll_and_click(selector=selector)
                    except TimeoutException:
                        print(f"Timeout exceeded for selector {selector}", file=sys.stderr)
                cls._applyColumns()
            cls._setColumnFilterDict(url_path=url_path, dict=url_path.get_false_dict())

    @classmethod
    def _getSingleColumnView(cls, column, url_path):
        if not isinstance(column, ColumnSelector):
            raise TypeError(f"Expected ColumnSelector enumeration member, but received {type(column)}")
        cls._getEmptyView(url_path)
        cls._editColumns()
        try:
            cls._scroll_and_click(selector=column.get_menu_selector())
        except TimeoutException:
            print(f"Timeout exceeded for selector {column.get_menu_selector()}", file=sys.stderr)
        cls._applyColumns()
        map = url_path.get_false_dict()
        map[column] = True
        cls._setColumnFilterDict(url_path=url_path, dict=map)

    @classmethod
    def _setColumnFilterDict(cls, url_path, dict = None):
        if cls._column_filter_dict is None:
            cls._column_filter_dict = url_path.get_default_dict()
        if dict is not None:
            for key, value in dict.items():
                if isinstance(key, ColumnSelector):
                    if isinstance(value, bool):
                        cls._column_filter_dict[key] = value
                    else:
                        raise TypeError(f"Expected bool, but received {type(value)}")
                else:
                    raise TypeError(f"Expected ColumnSelector enumeration member, but received {type(key)}")

    @classmethod
    def _getColumnData(cls, url_path, pages=range(1, 1)):
        if not isinstance(pages, range):
            raise TypeError(f"Expected range for pages, but received {type(pages)}")
        if pages.start < 1:
            raise ValueError(f"Page range is restricted to [1, infinity), received range [{pages.start}, {pages.stop})")
        if len(pages) == 0:
            pages = itertools.count(start=pages.start)
        outer_list = None
        names_list = None
        columnlist = url_path.get_django_available_columns();
        for page in pages:
            # try:
            tmp_outer_list = None
            tmp_names_list = None
            url = cls._url + "?page=" + str(page)
            if requests.get(url).status_code >= 400:
                return (names_list, outer_list)
            cls._browser.get(url)
            cls._setColumnFilterDict(url_path=url_path, dict=url_path.get_default_dict())
            if tmp_names_list is None:
                tmp_names_list = []
            page_name_list = cls._getShoeNames()
            if page_name_list is None:
                return (names_list, outer_list)
            else:
                tmp_names_list.extend(page_name_list)
            for column in columnlist:
                inner_list = []
                if not isinstance(column, ColumnSelector):
                    raise TypeError(f"Expected ColumnSelector enumeration member, but received {type(column)}")
                cls._getSingleColumnView(column, url_path)
                elements = cls._browser.find_elements(*column.get_data_selector())
                if elements is None or len(elements) < 1:
                    elements = [type('_WebElementPlaceholder', (object,), {'text': 'N/A'})() for _ in page_name_list]
                if tmp_outer_list is None:
                    tmp_outer_list = []
                for element in elements:
                    inner_list.append(url_path.get_column_lambda(column)(element.text))
                tmp_outer_list.append(inner_list)
            if names_list is None:
                names_list = []
            names_list.extend(tmp_names_list)
            if outer_list is None:
                outer_list = [[] for _ in range(len(tmp_outer_list))]
            outer_list_idx = 0
            for nested_list in tmp_outer_list:
                outer_list[outer_list_idx].extend(nested_list)
                outer_list_idx += 1
            # except TimeoutException as e:
                # print(e.msg, file=sys.stderr)
                # print(f"Skipping Page {page} from {url_path}", file=sys.stderr)
        return (names_list, outer_list)

    @classmethod
    def _getCsvStructure(cls, url_path, pages=None):
        csv_data = []
        if pages is None:
            shoe_names, data_list = cls._getColumnData(url_path=url_path)
        else:
            shoe_names, data_list = cls._getColumnData(pages=pages, url_path=url_path)
        for name in shoe_names:
            csv_data.append({"SHOE_NAME": name})
        columnlist = url_path.get_django_available_columns()
        columnlist_idx = 0
        for inner_list in data_list:
            if len(inner_list) != len(shoe_names):
                raise ValueError(f"Incongruent Lists: names list has length {len(shoe_names)}, but a list in the data list has length {len(inner_list)}")
            csv_data_idx = 0
            for item in inner_list:
                column = columnlist[columnlist_idx]
                column_name = url_path.get_column_name(column, display=True)
                csv_data[csv_data_idx][column_name] = item
                csv_data_idx += 1
            columnlist_idx += 1
        return csv_data

    @classmethod
    def _writeCSV(cls, filename, pages, url_path):
        filedata = cls._getCsvStructure(pages=pages, url_path=url_path)
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=filedata[0].keys(), lineterminator="\n")
            writer.writeheader()
            for row in filedata:
                writer.writerow(row)

    @classmethod
    def _scroll_and_click(cls, selector):
        # Change the selector type if necessary, e.g., By.ID, By.NAME, By.XPATH, etc.
        element = WebDriverWait(driver=cls._browser, timeout=cls._timeout).until(EC.visibility_of_element_located(selector))
        # Scroll the element into view
        cls._browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
        # Wait for the element to be clickable, and then click it
        WebDriverWait(driver=cls._browser, timeout=cls._timeout).until(EC.element_to_be_clickable(selector)).click()
        # Sleep after clicking
        time.sleep(cls._sleep)

    # Change view to table
    @classmethod
    def _getSlimListView(cls):
        cls._browser.get(cls._url)
        cookie = cls._browser.get_cookie("list_type")
        if cookie is None or cookie["value"] != "slim" or cookie["expiry"] < time.time():
            cls._scroll_and_click(selector=(By.CSS_SELECTOR, "svg.slim-view-icon.catalog__list-tab-icon"))

    @classmethod
    def _setTimeout(cls, timeout):
        if not isinstance(timeout, (int, float)):
            raise TypeError(f"Expected integer or floating-point for timeout, but received {type(timeout)}")
        if timeout < 0:
            raise ValueError(f"Expected non-negative value for timeout, but received {timeout}")
        cls._timeout = timeout

    @classmethod
    def _setSleep(cls, sleep):
        if not isinstance(sleep, (int, float)):
            raise TypeError(f"Expected integer or floating-point for sleep, but received {type(sleep)}")
        if sleep < 0:
            raise ValueError(f"Expected non-negative value for sleep, but received {sleep}")
        cls._sleep = sleep

    @classmethod
    def _setUrl(cls, url_path, gender):
        if not isinstance(url_path, Url_Paths):
            raise TypeError("url_path must be an enumeration member of type Url_Paths")
        if not isinstance(gender, Gender):
            raise TypeError("url_path must be an enumeration member of type Gender")
        cls._url += url_path.get_url_path(gender=gender)

    # PUBLIC INTERFACE METHOD
    @classmethod
    def scrape(cls, filename, url_path=Url_Paths.RUNNING_SHOES, gender=Gender.NONE, pages=None, sleep=None, timeout=None):
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")
        if not re.match(r'^(/[\w\s./-]+)*\/?[\w]+\.(csv)$', filename):
            raise ValueError("filename must be a full or relative path to a csv file (existing csv files will be overwritten)")
        cls._setUrl(url_path=url_path, gender=gender)
        if sleep is not None:
            cls._setSleep(sleep)
        if timeout is not None:
            cls._setTimeout(timeout)
        cls._getSlimListView()
        cls._writeCSV(filename=filename, pages=pages, url_path=url_path)
        cls._resetClassVariables()

    def __init__(self):
        pass

    # Set up Chromium options
    @classmethod
    def _getChromiumOptions(cls):
        chromium_options = Options()
# FIXME: Ensure the following is uncommented, do not commit or approve any PR with the next line commented out
        chromium_options.add_argument("--headless")
        chromium_options.add_argument("--no-sandbox")
        # /dev/shm is generally a tmpfs directory
        chromium_options.add_argument("--disable-dev-shm-usage")
        # Create a temporary directory for the user data
        temp_profile_dir = tempfile.mkdtemp()
        # Add the user data directory argument
        chromium_options.add_argument(f"--user-data-dir={temp_profile_dir}")
        chromium_options.binary_location = cls._chromium_location
        return chromium_options

    # Set up the browser
    @classmethod
    def _initBrowser(cls):
        service = Service(cls._driver_path)
        browser = webdriver.Chrome(service=service, options=cls._getChromiumOptions())
        browser.delete_all_cookies()
        cls._browser = browser
        atexit.register(cls._cleanup)

    def __new__(cls):
        if platform.system() != "Linux":
            raise RuntimeError("ScraperSingleton is only intended for Linux-based OSes")
        if cls._browser is None:
            cls._initBrowser()
        return cls
