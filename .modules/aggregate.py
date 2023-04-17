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
            value, available = member._value_
            member._value_ = value
            member.available = available
        return enum_class

class ColumnSelector(Enum, metaclass=ColumnSelectorEnumMeta):
    ARCH_SUPPORT = ("fact-arch-support", True)
    ARCH_TYPE = ("fact-arch-type", True)
    BRAND = ("fact-brand", True)
    CLEAT_DESIGN = ("fact-cleat-design", True)
    CLOSURE = ("fact-closure", True)
    COLLABORATION = ("fact-collaboration", True)
    COLLECTION = ("fact-collection", True)
    CONDITION = ("fact-condition", True)
    CONSTRUCTION = ("fact-construction", True)
    CUSHIONING = ("fact-cushioning", True)
    CUT = ("fact-cut", True)
    DESIGNED_BY = ("fact-designed-by", True)
    DISTANCE = ("fact-distance", True)
    DOWNTURN = ("fact-downturn", True)
    EMBELLISHMENT = ("fact-embellishment", True)
    ENVIRONMENT = ("fact-environment", True)
    EVENT = ("fact-event", True)
    EXPERT_RATING = ("fact-expert_score", True)
    FEATURE = ("fact-feature", True)
    FEATURES = ("fact-features", True)
    FIT = ("fact-fit", True)
    FOOT_CONDITION = ("fact-foot-condition", True)
    FOREFOOT_HEIGHT = ("fact-forefoot-height", True)
    FLEXIBILITY = ("fact-flexibility", True)
    GRAM_INSULATION = ("fact-gram-insulation", True)
    HEEL_HEIGHT = ("fact-heel-height", True)
    HEEL_TOE_DROP = ("fact-heel-to-toe-drop", True)
    INSPIRED_FROM = ("fact-inspired-from", True)
    LACE_TYPE = ("fact-lace-type", True)
    LACING_SYSTEM = ("fact-lacing-system", True)
    LAST_SHAPE = ("fact-last-shape", True)
    LEVEL = ("fact-level", True)
    LINING = ("fact-lining", True)
    LOCKDOWN = ("fact-lockdown", True)
    MSRP = ("fact-msrp_formatted", True)
    MATERIAL = ("fact-material", True)
    MIDSOLE = ("fact-midsole", True)
    NUMBER_OF_REVIEWS = ("fact-number-of-reviews", True)
    ORIGIN = ("fact-origin", True)
    ORTHOTIC_FRIENDLY = ("fact-orthotic-friendly", True)
    OUTSOLE = ("fact-outsole", True)
    PACE = ("fact-pace", True)
    PRINT = ("fact-print", True)
    PRONATION = ("fact-pronation", True)
    PROTECTION = ("fact-protection", True)
    RANDING = ("fact-randing", True)
    RELEASE_DATE = ("fact-release-date", True)
    REVIEW_TYPE = ("fact-review-type", True)
    RIGIDITY = ("fact-rigidity", True)
    SALES_PRICE = ("fact-price", True)
    SCORE = ("fact-score", True)
    SEASON = ("fact-season", True)
    SENSITIVITY = ("fact-sensitivity", True)
    SHOE_TYPE = ("fact-shoe-type", True)
    SIGNATURE = ("fact-signature", True)
    SPIKE_SIZE = ("fact-spike-size", True)
    SPIKE_TYPE = ("fact-spike-type", True)
    STIFFNESS = ("fact-stiffness", True)
    STRETCH = ("fact-stretch", True)
    STRIKE_PATTERN = ("fact-strike-pattern", True)
    STUD_TYPE = ("fact-stud-type", True)
    STYLE = ("fact-style", True)
    SUMMER = ("fact-summer", True)
    SURFACE = ("fact-surface", True)
    SUPPORT = ("fact-support", True)
    TERRAIN = ("fact-terrain", True)
    TECHNOLOGY = ("fact-technology", True)
    THICKNESS = ("fact-thickness", True)
    TOEBOX = ("fact-toebox", True)
    TONGUE_PULL_LOOP = ("fact-tongue-pull-loop", True)
    TOP = ("fact-top", True)
    TYPE = ("fact-type", True)
    ULTRA_RUNNING = ("fact-ultra-running", True)
    USE = ("fact-use", True)
    USER_RATING = ("fact-users_score", True)
    WATERPROOFING = ("fact-waterproofing", True)
    WEIGHT = ("fact-weight", True)
    WIDTH = ("fact-width", True)
    WORN_BY = ("fact-worn-by", True)
    ZERO_DROP = ("fact-zero-drop", True)

    @classmethod
    def _reset_availability(cls, val=True):
        if not isinstance(val, bool):
            raise TypeError(f"Expected bool for val, but received {type(val)}")
        for member in cls:
            member.available = val

    # set availability to false for all enumeration members except those in include list
    @classmethod
    def includeOnly(cls, include):
        if not isinstance(include, list):
            raise TypeError(f"Expected include to be a list, but recieved {type(include)}")
        cls._reset_availability(val=False)
        for member in include:
            if isinstance(member, cls):
                member.available = True

    @classmethod
    def get_full_list(cls, exclude=None):
        if exclude is None:
            exclude = []
        return [member.name for member in cls if member not in exclude and member.available]

    @classmethod
    def get_empty_list(cls, include=None):
        if include is None:
            include = []
        return [member.name for member in include if isinstance(member, cls) and member.available]

    @classmethod
    def get_full_menu_selector_list(cls, exclude=None):
        if exclude is None:
            exclude = []
        return [column_selector.get_menu_selector() for column_selector in cls if column_selector not in exclude and column_selector.available]

    @classmethod
    def get_empty_menu_selector_list(cls, include=None):
        if include is None:
            include = []
        return [column_selector.get_menu_selector() for column_selector in include if isinstance(column_selector, cls) and column_selector.available]

    @classmethod
    def get_default_map(cls):
        default_map = {}
        for member in cls:
            if member.available:
                default_map[member] = True
        if cls.MSRP.available:
            default_map[cls.MSRP] = False
        return default_map

    @classmethod
    def get_true_map(cls):
        false_map = cls.get_default_map()
        if cls.MSRP.available:
            false_map[cls.MSRP] = True
        return false_map

    @classmethod
    def get_false_map(cls):
        true_map = cls.get_true_map()
        for key in true_map:
            true_map[key] = False
        return true_map

    def get_menu_selector(self):
        return (By.CSS_SELECTOR, f"input[type='checkbox'][id='{self.value}'] + span.checkbox")

    def get_data_selector(self):
        if self == ColumnSelector.SCORE:
            return (By.CSS_SELECTOR, "div.catalog-list-slim__facts__column div.catalog-list-slim__shoes-fact__values.corescore__values div.corescore div.corescore__score.score_green")
        else:
            return (By.CSS_SELECTOR, "div.catalog-list-slim__facts__column div.catalog-list-slim__shoes-fact__values span")

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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": models.CharField(max_length=32, choices=(('waterproof', "Waterproof"), ('water resistant', "Water Resistant")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Waterproof' if 'waterproof' in s.lower() else 'Water Resistant' if re.search(r'water\s*resistant', s.lower()) else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "lambda_serializer": lambda s: True if re.search(r'size\s*stretch' in s.lower()) else False if re.search(r'no\s*stretch', s.lower()) else None
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda x: (round(sum(map(float, x.rstrip("mm").split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
            ColumnSelector.HEEL_HEIGHT: {
                "name": "Heel Height",
                "units": "mm",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda x: (round(sum(map(float, x.rstrip("mm").split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "name": "Heel to Toe Drop",
                "units": "mm",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda x: (round(sum(map(float, x.rstrip("mm").split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "lambda_serializer": lambda s: '{' + ', '.join(format(None, ['Laces' if 'laces' in s.lower() else None, 'Slip-On' if 'slip-on' in s.lower() else None, 'BOA' if 'boa' in s.lower() else None])).rstrip(', ') + '}'
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
                "lambda_serializer": lambda s: '{' + ', '.join(format(None, ['Cheap' if 'cheap' in s.lower() else None, 'Breathable' if 'breathable' in s.lower() else None, 'Expensive' if 'expensive' in s.lower() else None])).rstrip(', ') + '}'
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.MATERIAL: {
                "name": "Material",
                "units": None,
                "django_model": ArrayField(models.CharField(max_length=16, choices=(('leather', "Leather"), ('synthetic', "Synthetic"), ('knit', "Knit"), ('ortholite', "Ortholite"))), blank=True, null=True),
                "lambda_serializer": lambda s: '{' + ', '.join(format(None, ['Leather' if 'leather' in s.lower() else None, 'Synthetic' if 'synthetic' in s.lower() else None, 'Knit' if 'knit' in s.lower() else None, 'Ortholite' if 'ortholite' in s.lower() else None])).rstrip(', ') + '}'
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": models.CharField(max_length=16, choices=(('USA', "USA"), ('European', "European"), ('Italian', "Italian"), ('German', "German")), blank=True, null=True),
                "lambda_serializer": lambda s: 'USA' if 'usa' in s.lower() else 'European' if 'european' in s.lower() else 'Italian' if 'italian' in s.lower() else 'German' if 'german' in s.lower() else None
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
                "django_model": models.CharField(choices=(('waterproof', "Waterproof"), ('water repellent', 'Water Repellent')), blank=True, null=True),
                "lambda_serializer": lambda s: 'Water Repellent' if 'repellent' in s.lower() else 'Waterproof' if 'waterproof' in s.lower() else None
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": models.CharField(max_length=5, choices=(('laces', "Laces"), ('slip on', "Slip On")), blank=True, null=True),
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
                "django_model": models.CharField(max_length=5, choices=(('low', "Low"), ('mid', "Mid")), blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('supination', 'Supination'), ('underpronation', 'Underpronation'), ('neutral', 'Neutral'), ('overpronation', 'Overpronation'), ('severe overpronation'), ('Severe Overpronation'))), blank=True, null=True),
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": None, # FIXME: models.CharField(max_length=16, choices=(("stability", "Stability"), ("neutral", "Neutral"), ("motion control", "Motion control")), blank=True, null=True))
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
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
                "django_model": models.CharField(max_length=24, choices=(('rigid', "Very stiff"), ('semi-rigid', "Stiff"), ('balanced', "Moderate"), ('semi-flexible', "Flexible"), ('flexible', "Very flexible")), blank=True, null=True),
                "lambda_serializer": lambda s: 'Very stiff' if 'very stiff' in s.lower() else 'Stiff' if 'stiff' in s.lower() else 'Moderate' if 'moderate' in s.lower() else 'Flexible' if any(match.group(2) and not match.group(1) for match in re.finditer(r'(very\s*)?(flexible)', s.lower())) else 'Very flexible' if re.search(r'very\s*flexible', s.lower()) else None
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda x: (round(sum(map(float, x.rstrip("mm").split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_HEIGHT: {
                "name": "Heel Height",
                "units": "mm",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda x: (round(sum(map(float, x.rstrip("mm").split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "name": "Heel to Toe Drop",
                "units": "mm",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda x: (round(sum(map(float, x.rstrip("mm").split("-"))) / (2.0 if "-" in x else 1.0), 1) if 'mm' in x else None)
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
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": ArrayField(models.CharField(max_length=32, choices=(('supination', 'Supination'), ('underpronation', 'Underpronation'), ('neutral', 'Neutral'), ('overpronation', 'Overpronation'), ('severe overpronation'), ('Severe Overpronation'))), blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
            # TODO: Continue from here
            ColumnSelector.LACE_TYPE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ORIGIN: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PRINT: {
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.STYLE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOP: {
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SURFACE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOP: {
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CONSTRUCTION: {
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.EVENT: {
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FEATURES: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SPIKE_TYPE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SURFACE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FOREFOOT_HEIGHT: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.HEEL_HEIGHT: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            }
        }
    )
    TRAIL_SHOES = (
        "trail-running-shoes",
        {
            ColumnSelector.ARCH_SUPPORT: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ARCH_TYPE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CUSHIONING: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.DISTANCE: {
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FLEXIBILITY: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FOOT_CONDITION: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.FOREFOOT_HEIGHT: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.HEEL_HEIGHT: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.HEEL_TOE_DROP: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
                "lambda_serializer": lambda x: None if '$' not in x.lower() else '{:.2f}'.format(float(x.strip('$')))
            },
            ColumnSelector.NUMBER_OF_REVIEWS: {
                "name": "Number of Reviews",
                "units": None,
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PACE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.PRONATION: {
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.STRIKE_PATTERN: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.SUMMER: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TECHNOLOGY: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TERRAIN: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOEBOX: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TYPE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.ULTRA_RUNNING: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.WEIGHT: {
                "name": "Weight",
                "units": "oz",
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            },
            ColumnSelector.WIDTH: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            }
        }
    )
    WALKING_SHOES = (
        "walking-shoes",
        {
            ColumnSelector.ARCH_SUPPORT: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.BRAND: {
                "name": "Brand",
                "units": None,
                "django_model": models.CharField(max_length=32, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CLOSURE: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.COLLECTION: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.CONDITION: {
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MATERIAL: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.MSRP: {
                "name": "MSRP",
                "units": "USD",
                "django_model": models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True),
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
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.TOEBOX: {
                "django_model": None,
                "lambda_serializer": lambda s: None if 'n/a' in s.lower() else s
            },
            ColumnSelector.USE: {
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
                "django_model": models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True),
                "lambda_serializer": lambda s: None if 'oz' not in s.lower() else round(float(''.join(filter(lambda c: c.isdigit() or c == '.', s))), 1)
            }
        }
    )

    def get_column_name(self, column, attribute = False, display = False):
        if isinstance(column, ColumnSelector):
            name = self.filterdict[column]["name"]
            if attribute:
                name = name.lower().replace(' ', '_')
            elif display:
                units = self.get_column_units(column)
                if units is not None:
                    name += f" ({units}))"
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
        return self.filterdict.keys()

    def get_django_available_columns(self):
        retlist = []
        for column, obj in self.filterdict.items():
            if obj["django_model"] is not None:
                retlist.append(column)
        return retlist

    @classmethod
    def get_include_dict(cls):
        include = {}
        for member in cls:
            include[member] = member.get_available_columns()
        return include

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

    def setColumnSelectorAvailability(self):
        ColumnSelector.includeOnly(include=self.get_available_columns())

class ScraperSingleton:
    _browser = None
    _chromium_location = "/usr/bin/chromium"
    _column_filter_dict = None
    _domain = "runrepeat.com"
    _driver_path = "/usr/bin/chromedriver"
    _sleep = 0.5
    _timeout = 10
    _url = f"https://{_domain}"

    @classmethod
    def _cleanup(cls):
        if cls._browser is not None:
            cls._browser.quit()

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
    def _getColumnFilterDict(cls):
        if cls._column_filter_dict is None:
            cls._column_filter_dict = ColumnSelector.get_default_map()
        return cls._column_filter_dict

    @classmethod
    def _getEmptyView(cls):
        checkboxes = None
        filter_dict = cls._getColumnFilterDict()
        if not filter_dict == ColumnSelector.get_false_map():
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
                        raise TimeoutException(msg=f"Timeout exceeded for selector {selector}")
                cls._applyColumns()
            cls._setColumnFilterDict(ColumnSelector.get_false_map())

    @classmethod
    def _getSingleColumnView(cls, column):
        if not isinstance(column, ColumnSelector):
            raise TypeError(f"Expected ColumnSelector enumeration member, but received {type(column)}")
        cls._getEmptyView()
        cls._editColumns()
        try:
            cls._scroll_and_click(selector=column.get_menu_selector())
        except TimeoutException:
            raise TimeoutException(msg=f"Timeout exceeded for selector {column.get_menu_selector()}")
        cls._applyColumns()
        map = ColumnSelector.get_false_map()
        map[column] = True
        cls._setColumnFilterDict(map)

    @classmethod
    def _setColumnFilterDict(cls, dict):
        if cls._column_filter_dict is None:
            cls._column_filter_dict = ColumnSelector.get_default_map()
        for key, value in dict.items():
            if isinstance(key, ColumnSelector):
                if isinstance(value, bool):
                    cls._column_filter_dict[key] = value
                else:
                    raise TypeError(f"Expected bool, but received {type(value)}")
            else:
                raise TypeError(f"Expected ColumnSelector enumeration member, but received {type(key)}")

    @classmethod
    def _getColumnData(cls, column_list, url_path, pages=range(1, 1)):
        if not isinstance(pages, range):
            raise TypeError(f"Expected range for pages, but received {type(pages)}")
        if pages.start < 1:
            raise ValueError(f"Page range is restricted to [1, infinity), received range [{pages.start}, {pages.stop})")
        if len(pages) == 0:
            pages = itertools.count(start=pages.start)
        outer_list = None
        names_list = None
        for page in pages:
            try:
                tmp_outer_list = None
                tmp_names_list = None
                cls._browser.get(cls._url + "?page=" + str(page))
                cls._setColumnFilterDict(ColumnSelector.get_default_map())
                if tmp_names_list is None:
                    tmp_names_list = []
                for name in cls._getShoeNames():
                    tmp_names_list.append(name)
                for column in column_list:
                    inner_list = []
                    if not isinstance(column, ColumnSelector):
                        raise TypeError(f"Expected ColumnSelector enumeration member, but received {type(column)}")
                    cls._getSingleColumnView(column)
                    elements = cls._browser.find_elements(*column.get_data_selector())
                    if len(elements) < 1:
                        return (names_list, outer_list)
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
            except TimeoutException as e:
                print(e.msg, file=sys.stderr)
                print(f"Skipping Page {page}", file=sys.stderr)
        return (names_list, outer_list)

    @classmethod
    def _getCsvStructure(cls, columnlist, url_path, pages=None):
        csv_data = []
        if pages is None:
            shoe_names, data_list = cls._getColumnData(column_list=columnlist, url_path=url_path)
        else:
            shoe_names, data_list = cls._getColumnData(column_list=columnlist, pages=pages, url_path=url_path)
        for name in shoe_names:
            csv_data.append({"SHOE_NAME": name})
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
    def _writeCSV(cls, filename, columnlist, pages, url_path):
        filedata = cls._getCsvStructure(columnlist=columnlist, pages=pages, url_path=url_path)
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

    @staticmethod
    def _validateUserColumnList(columnlist):
        if not isinstance(columnlist, list):
            raise TypeError(f"Expected list, but received {type(columnlist)}")
        for member in columnlist:
            if not isinstance(member, ColumnSelector):
                raise TypeError(f"Expected ColumnSelector enumeration member in list, but received {type(member)}")
            if not member.available:
                raise ValueError(f"Column {member.name} not available for the current shoe-type")

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
        url_path.setColumnSelectorAvailability()

    # PUBLIC INTERFACE METHOD
    @classmethod
    def scrape(cls, filename, columnlist=None, url_path=Url_Paths.RUNNING_SHOES, gender=Gender.NONE, pages=None, sleep=None, timeout=None):
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")
        if not re.match(r'^(/[\w\s./-]+)*\/?[\w]+\.(csv)$', filename):
            raise ValueError("filename must be a full or relative path to a csv file (existing csv files will be overwritten)")
        if columnlist is None:
            columnlist = url_path.get_django_available_columns()
        if url_path == Url_Paths.SOCCER_CLEATS and ColumnSelector.FEATURES in columnlist:
            print("INFO: FEATURES column for SOCCER_CLEATS contains Price-Tier data")
        cls._setUrl(url_path=url_path, gender=gender)
        if sleep is not None:
            cls._setSleep(sleep)
        if timeout is not None:
            cls._setTimeout(timeout)
        cls._validateUserColumnList(columnlist)
        cls._getSlimListView()
        cls._writeCSV(filename=filename, columnlist=columnlist, pages=pages, url_path=url_path)

    def __init__(self):
        pass

    # Set up Chromium options
    @classmethod
    def _getChromiumOptions(cls):
        chromium_options = Options()
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
