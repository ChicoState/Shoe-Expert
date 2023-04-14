import atexit
import csv
import datetime
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
            value, available, regex, django_model = member._value_
            member._value_ = value
            member.available = available
            member.regex = regex
            member.django_model = django_model
        return enum_class

class ColumnSelector(Enum, metaclass=ColumnSelectorEnumMeta):
    ARCH_SUPPORT = ("fact-arch-support", True, None, models.IntegerField(choices=((0, "Stability"), (1, "Neutral"), (2, "Motion control")), blank=True, null=True))
    ARCH_TYPE = ("fact-arch-type", True, None, models.IntegerField(choices=((0, "Low"), (2, "High")), blank=True, null=True))
    BRAND = ("fact-brand", True, None, models.CharField(max_length=32, blank=True, null=True))
    CLEAT_DESIGN = ("fact-cleat-design", True, None, None)
    CLOSURE = ("fact-closure", True, None, None)
    COLLABORATION = ("fact-collaboration", True, None, None)
    COLLECTION = ("fact-collection", True, None, None)
    CONDITION = ("fact-condition", True, None, None)
    CONSTRUCTION = ("fact-construction", True, None, None)
    CUSHIONING = ("fact-cushioning", True, None, models.IntegerField(choices=((1, "Firm"), (2, "Balanced"), (3, "Plush")), blank=True, null=True))
    CUT = ("fact-cut", True, None, None)
    DESIGNED_BY = ("fact-designed-by", True, None, None)
    DISTANCE = ("fact-distance", True, None, None)
    DOWNTURN = ("fact-downturn", True, None, None)
    EMBELLISHMENT = ("fact-embellishment", True, None, None)
    ENVIRONMENT = ("fact-environment", True, None, None)
    EVENT = ("fact-event", True, None, None)
    EXPERT_RATING = ("fact-expert_score", True, None, None)
    FEATURE = ("fact-feature", True, None, None)
    FEATURES = ("fact-features", True, None, None)
    FIT = ("fact-fit", True, None, None)
    FOOT_CONDITION = ("fact-foot-condition", True, None, None)
    FOREFOOT_HEIGHT = ("fact-forefoot-height", True, None, models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True))
    FLEXIBILITY = ("fact-flexibility", True, None, models.IntegerField(choices=((1, "Very stiff"), (2, "Stiff"), (3, "Moderate"), (4, "Flexible"), (5, "Very flexible")), blank=True, null=True))
    GRAM_INSULATION = ("fact-gram-insulation", True, None, None)
    HEEL_HEIGHT = ("fact-heel-height", True, None, models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True))
    HEEL_TOE_DROP = ("fact-heel-to-toe-drop", True, None, models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True))
    INSPIRED_FROM = ("fact-inspired-from", True, None, None)
    LACE_TYPE = ("fact-lace-type", True, None, None)
    LACING_SYSTEM = ("fact-lacing-system", True, None, None)
    LAST_SHAPE = ("fact-last-shape", True, None, None)
    LEVEL = ("fact-level", True, None, None)
    LINING = ("fact-lining", True, None, None)
    LOCKDOWN = ("fact-lockdown", True, None, None)
    MSRP = ("fact-msrp_formatted", True, None, models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True))
    MATERIAL = ("fact-material", True, None, None)
    MIDSOLE = ("fact-midsole", True, None, None)
    NUMBER_OF_REVIEWS = ("fact-number-of-reviews", True, None, None)
    ORIGIN = ("fact-origin", True, None, None)
    ORTHOTIC_FRIENDLY = ("fact-orthotic-friendly", True, None, None)
    OUTSOLE = ("fact-outsole", True, None, None)
    PACE = ("fact-pace", True, None, None)
    PRINT = ("fact-print", True, None, None)
    PRONATION = ("fact-pronation", True, None, models.CharField(max_length=256, blank=True, null=True))
    PROTECTION = ("fact-protection", True, None, None)
    RANDING = ("fact-randing", True, None, None)
    RELEASE_DATE = ("fact-release-date", True, None, models.PositiveIntegerField(validators=[MinValueValidator(1970), MaxValueValidator(datetime.today().year + 1)], blank=True, null=True))
    REVIEW_TYPE = ("fact-review-type", True, None, None)
    RIGIDITY = ("fact-rigidity", True, None, None)
    SALES_PRICE = ("fact-price", True, None, None)
    SCORE = ("fact-score", True, None, None)
    SEASON = ("fact-season", True, None, None)
    SENSITIVITY = ("fact-sensitivity", True, None, None)
    SHOE_TYPE = ("fact-shoe-type", True, None, None)
    SIGNATURE = ("fact-signature", True, None, None)
    SPIKE_SIZE = ("fact-spike-size", True, None, None)
    SPIKE_TYPE = ("fact-spike-type", True, None, None)
    STIFFNESS = ("fact-stiffness", True, None, None)
    STRETCH = ("fact-stretch", True, None, None)
    STRIKE_PATTERN = ("fact-strike-pattern", True, None, models.CharField(max_length=128, blank=True, null=True))
    STUD_TYPE = ("fact-stud-type", True, None, None)
    STYLE = ("fact-style", True, None, None)
    SUMMER = ("fact-summer", True, None, None)
    SURFACE = ("fact-surface", True, None, None)
    SUPPORT = ("fact-support", True, None, None)
    TERRAIN = ("fact-terrain", True, None, models.IntegerField(choices=((1, "Road"), (2, "Trail")), blank=True, null=True))
    TECHNOLOGY = ("fact-technology", True, None, None)
    THICKNESS = ("fact-thickness", True, None, models.IntegerField(choices=((1, "Narrow"), (2, "Medium"), (3, "Wide"), (4, "Extra Wide")), blank=True, null=True))
    TOEBOX = ("fact-toebox", True, None, None)
    TONGUE_PULL_LOOP = ("fact-tongue-pull-loop", True, None, None)
    TOP = ("fact-top", True, None, None)
    TYPE = ("fact-type", True, None, None)
    ULTRA_RUNNING = ("fact-ultra-running", True, None, None)
    USE = ("fact-use", True, None, None)
    USER_RATING = ("fact-users_score", True, None, None)
    WATERPROOFING = ("fact-waterproofing", True, None, None)
    WEIGHT = ("fact-weight", True, None, models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True))
    WIDTH = ("fact-width", True, None, models.CharField(max_length=128, blank=True, null=True))
    WORN_BY = ("fact-worn-by", True, None, None)
    ZERO_DROP = ("fact-zero-drop", True, None, None)

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
            value, filterlist = member._value_
            member._value_ = value
            member.filterlist = filterlist
        return enum_class

class Url_Paths(Enum, metaclass=Url_PathsEnumMeta):
    APPROACH_SHOES = (
        "approach-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.MSRP,
            ColumnSelector.MATERIAL,
            ColumnSelector.PROTECTION,
            ColumnSelector.RANDING,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SENSITIVITY,
            ColumnSelector.SUPPORT,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.TOP,
            ColumnSelector.USER_RATING,
            ColumnSelector.WATERPROOFING,
            ColumnSelector.WEIGHT
        ]
    )
    BASKETBALL_SHOES = (
        "basketball-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.LOCKDOWN,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SIGNATURE,
            ColumnSelector.TOP,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT
        ]
    )
    CLIMBING_SHOES = (
        "climbing-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.CONSTRUCTION,
            ColumnSelector.DOWNTURN,
            ColumnSelector.ENVIRONMENT,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.FIT,
            ColumnSelector.LAST_SHAPE,
            ColumnSelector.LEVEL,
            ColumnSelector.LINING,
            ColumnSelector.MSRP,
            ColumnSelector.MATERIAL,
            ColumnSelector.MIDSOLE,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.STIFFNESS,
            ColumnSelector.STRETCH,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.THICKNESS,
            ColumnSelector.TONGUE_PULL_LOOP,
            ColumnSelector.TOP,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WORN_BY
        ]
    )
    CROSSFIT_SHOES = (
        "crossfit-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.FOREFOOT_HEIGHT,
            ColumnSelector.HEEL_HEIGHT,
            ColumnSelector.HEEL_TOE_DROP,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.TOEBOX,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WIDTH
        ]
    )
    CYCLING_SHOES = (
        "cycling-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLEAT_DESIGN,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURE,
            ColumnSelector.FEATURES,
            ColumnSelector.MSRP,
            ColumnSelector.MATERIAL,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.RIGIDITY,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT
        ]
    )
    FOOTBALL_CLEATS = (
        "football-cleats",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.STRIKE_PATTERN,
            ColumnSelector.STUD_TYPE,
            ColumnSelector.TOP,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WIDTH
        ]
    )
    GOLF_SHOES = (
        "golf-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.MSRP,
            ColumnSelector.MATERIAL,
            ColumnSelector.OUTSOLE,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.STYLE,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.USER_RATING,
            ColumnSelector.WATERPROOFING,
            ColumnSelector.WEIGHT
        ]
    )
    HIKING_BOOTS = (
        "hiking-boots",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.CONSTRUCTION,
            ColumnSelector.CUT,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.FIT,
            ColumnSelector.FOOT_CONDITION,
            ColumnSelector.GRAM_INSULATION,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.ORIGIN,
            ColumnSelector.ORTHOTIC_FRIENDLY,
            ColumnSelector.PRONATION,
            ColumnSelector.PROTECTION,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SEASON,
            ColumnSelector.SUPPORT,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.ULTRA_RUNNING,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WATERPROOFING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WIDTH,
            ColumnSelector.ZERO_DROP
        ]
    )
    HIKING_SHOES = (
        "hiking-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.CONSTRUCTION,
            ColumnSelector.CUT,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.FIT,
            ColumnSelector.FOOT_CONDITION,
            ColumnSelector.GRAM_INSULATION,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.ORIGIN,
            ColumnSelector.PRONATION,
            ColumnSelector.PROTECTION,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SEASON,
            ColumnSelector.SUPPORT,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WATERPROOFING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WIDTH
        ]
    )
    RUNNING_SHOES = (
        "running-shoes",
        [
            ColumnSelector.ARCH_SUPPORT,
            ColumnSelector.ARCH_TYPE,
            ColumnSelector.BRAND,
            ColumnSelector.COLLECTION,
            ColumnSelector.CUSHIONING,
            ColumnSelector.DISTANCE,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.FLEXIBILITY,
            ColumnSelector.FOOT_CONDITION,
            ColumnSelector.FOREFOOT_HEIGHT,
            ColumnSelector.HEEL_HEIGHT,
            ColumnSelector.HEEL_TOE_DROP,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.PACE,
            ColumnSelector.PRONATION,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SEASON,
            ColumnSelector.STRIKE_PATTERN,
            ColumnSelector.SUMMER,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.TERRAIN,
            ColumnSelector.TOEBOX,
            ColumnSelector.TYPE,
            ColumnSelector.ULTRA_RUNNING,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WATERPROOFING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WIDTH
        ]
    )
    SNEAKERS = (
        "sneakers",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLABORATION,
            ColumnSelector.COLLECTION,
            ColumnSelector.DESIGNED_BY,
            ColumnSelector.EMBELLISHMENT,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.INSPIRED_FROM,
            ColumnSelector.LACE_TYPE,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.ORIGIN,
            ColumnSelector.PRINT,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SEASON,
            ColumnSelector.STYLE,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.TOP,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT
        ]
    )
    SOCCER_CLEATS = (
        "soccer-cleats",
        [
            ColumnSelector.BRAND,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.LACING_SYSTEM,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.FEATURES,            # PRICE TIER
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SIGNATURE,
            ColumnSelector.SURFACE,
            ColumnSelector.TOP,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT
        ]
    )
    TENNIS_SHOES = (
        "tennis-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.COLLABORATION,
            ColumnSelector.COLLECTION,
            ColumnSelector.CONSTRUCTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURE,
            ColumnSelector.FEATURES,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SHOE_TYPE,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT
        ]
    )
    TRACK_SHOES = (
        "track-and-field-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.EVENT,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURE,
            ColumnSelector.FEATURES,
            ColumnSelector.MSRP,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SPIKE_SIZE,
            ColumnSelector.SPIKE_TYPE,
            ColumnSelector.SURFACE,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT
        ]
    )
    TRAINING_SHOES = (
        "training-shoes",
        [
            ColumnSelector.BRAND,
            ColumnSelector.COLLECTION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.FOREFOOT_HEIGHT,
            ColumnSelector.HEEL_HEIGHT,
            ColumnSelector.HEEL_TOE_DROP,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.TOEBOX,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WIDTH
        ]
    )
    TRAIL_SHOES = (
        "trail-running-shoes",
        [
            ColumnSelector.ARCH_SUPPORT,
            ColumnSelector.ARCH_TYPE,
            ColumnSelector.BRAND,
            ColumnSelector.COLLECTION,
            ColumnSelector.CUSHIONING,
            ColumnSelector.DISTANCE,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.FLEXIBILITY,
            ColumnSelector.FOOT_CONDITION,
            ColumnSelector.FOREFOOT_HEIGHT,
            ColumnSelector.HEEL_HEIGHT,
            ColumnSelector.HEEL_TOE_DROP,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.NUMBER_OF_REVIEWS,
            ColumnSelector.PACE,
            ColumnSelector.PRONATION,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SEASON,
            ColumnSelector.STRIKE_PATTERN,
            ColumnSelector.SUMMER,
            ColumnSelector.TECHNOLOGY,
            ColumnSelector.TERRAIN,
            ColumnSelector.TOEBOX,
            ColumnSelector.TYPE,
            ColumnSelector.ULTRA_RUNNING,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WATERPROOFING,
            ColumnSelector.WEIGHT,
            ColumnSelector.WIDTH
        ]
    )
    WALKING_SHOES = (
        "walking-shoes",
        [
            ColumnSelector.ARCH_SUPPORT,
            ColumnSelector.BRAND,
            ColumnSelector.CLOSURE,
            ColumnSelector.COLLECTION,
            ColumnSelector.CONDITION,
            ColumnSelector.EXPERT_RATING,
            ColumnSelector.FEATURES,
            ColumnSelector.MATERIAL,
            ColumnSelector.MSRP,
            ColumnSelector.RELEASE_DATE,
            ColumnSelector.REVIEW_TYPE,
            ColumnSelector.SALES_PRICE,
            ColumnSelector.SCORE,
            ColumnSelector.SURFACE,
            ColumnSelector.TOEBOX,
            ColumnSelector.USE,
            ColumnSelector.USER_RATING,
            ColumnSelector.WEIGHT
        ]
    )

    def get_available_columns(self):
        return self.filterlist

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
    def _getColumnData(cls, column_list, pages=range(1, 1)):
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
                for item in column_list:
                    inner_list = []
                    if not isinstance(item, ColumnSelector):
                        raise TypeError(f"Expected ColumnSelector enumeration member, but received {type(item)}")
                    cls._getSingleColumnView(item)
                    elements = cls._browser.find_elements(*item.get_data_selector())
                    if len(elements) < 1:
                        return (names_list, outer_list)
                    if tmp_outer_list is None:
                        tmp_outer_list = []
                    for element in elements:
                        inner_list.append(element.text)
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
    def _getCsvStructure(cls, columnlist, pages=None):
        csv_data = []
        if pages is None:
            shoe_names, data_list = cls._getColumnData(column_list=columnlist)
        else:
            shoe_names, data_list = cls._getColumnData(column_list=columnlist, pages=pages)
        for name in shoe_names:
            csv_data.append({"SHOE_NAME": name})
        columnlist_idx = 0
        for inner_list in data_list:
            if len(inner_list) != len(shoe_names):
                raise ValueError(f"Incongruent Lists: names list has length {len(shoe_names)}, but a list in the data list has length {len(inner_list)}")
            csv_data_idx = 0
            for item in inner_list:
                csv_data[csv_data_idx][columnlist[columnlist_idx].name] = item
                csv_data_idx += 1
            columnlist_idx += 1
        return csv_data

    @classmethod
    def _writeCSV(cls, filename, columnlist, pages):
        filedata = cls._getCsvStructure(columnlist=columnlist, pages=pages)
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
        if url_path == Url_Paths.SOCCER_CLEATS and ColumnSelector.FEATURES in columnlist:
            print("INFO: FEATURES column for SOCCER_CLEATS contains Price-Tier data")
        cls._setUrl(url_path=url_path, gender=gender)
        if columnlist is None:
            columnlist = url_path.get_available_columns()
        if sleep is not None:
            cls._setSleep(sleep)
        if timeout is not None:
            cls._setTimeout(timeout)
        cls._validateUserColumnList(columnlist)
        cls._getSlimListView()
        cls._writeCSV(filename=filename, columnlist=columnlist, pages=pages)

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
