# TODO: continue adding exclude lists, start at CYCLING_SHOES
from enum import Enum, EnumMeta
import os
import platform
from pprint import PrettyPrinter
import re
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import tempfile
import time

class ScraperSingleton:
    __browser = None
    __chromium_location = "/usr/bin/chromium"
    __column_filter_dict = None
    __domain = "runrepeat.com"
    __driver_path = "/usr/bin/chromedriver"
    __sleep = 1
    __url = "https://" + __domain
    __wait = 15

    class __AvailableEnumMeta(EnumMeta):
        def __call__(cls, value, *args, **kwargs):
            member = super().__call__(value, *args, **kwargs)
            if not member.available:
                raise ValueError(f"{member.name} is not available")
            return member

    class ColumnSelector(Enum, metaclass=__AvailableEnumMeta):
        ARCH_SUPPORT = ("fact-arch-support", True)
        ARCH_TYPE = ("fact-arch-type", True)
        BRAND = ("fact-brand", True)
        CLOSURE = ("fact-closure", True)
        COLLABORATION = ("fact-collaboration", True)
        COLLECTION = ("fact-collection", True)
        CONDITION = ("fact-condition", True)
        CONSTRUCTION = ("fact-construction", True)
        CUSHIONING = ("fact-cushioning", True)
        CUT = ("fact-cut", True)
        DESIGNED_BY = ("fact-designed-by", True)
        DISTANCE = ("fact-distance", True)
        EMBELLISHMENT = ("fact-embellishment", True)
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
        LOCKDOWN = ("fact-lockdown", True)
        MSRP = ("fact-msrp_formatted", True)
        MATERIAL = ("fact-material", True)
        NUMBER_OF_REVIEWS = ("fact-number-of-reviews", True)
        ORIGIN = ("fact-origin", True)
        ORTHOTIC_FRIENDLY = ("fact-orthotic-friendly", True)
        PACE = ("fact-pace", True)
        PRICE_TIER = ("fact-features", True)
        PRINT = ("fact-print", True)
        PRONATION = ("fact-pronation", True)
        PROTECTION = ("fact-protection", True)
        RELEASE_DATE = ("fact-release-date", True)
        REVIEW_TYPE = ("fact-review-type", True)
        SALES_PRICE = ("fact-price", True)
        SCORE = ("fact-score", True)
        SEASON = ("fact-season", True)
        SHOE_TYPE = ("fact-shoe-type", True)
        SIGNATURE = ("fact-signature", True)
        SPIKE_SIZE = ("fact-spike-size", True)
        SPIKE_TYPE = ("fact-spike-type", True)
        STRIKE_PATTERN = ("fact-strike-pattern", True)
        STUD_TYPE = ("fact-stud-type", True)
        STYLE = ("fact-style", True)
        SUMMER = ("fact-summer", True)
        SURFACE = ("fact-surface", True)
        SUPPORT = ("fact-support", True)
        TERRAIN = ("fact-terrain", True)
        TECHNOLOGY = ("fact-technology", True)
        TOEBOX = ("fact-toebox", True)
        TOP = ("fact-top", True)
        TYPE = ("fact-type", True)
        ULTRA_RUNNING = ("fact-ultra-running", True)
        USE = ("fact-use", True)
        USER_RATING = ("fact-users_score", True)
        WATERPROOFING = ("fact-waterproofing", True)
        WEIGHT = ("fact-weight", True)
        WIDTH = ("fact-width", True)
        ZERO_DROP = ("fact-zero-drop", True)

        def __init__(self, value, available):
            super().__init__(value)
            self.available = available

        # set availability to false for a list of enumeration members
        @classmethod
        def __exclude(cls, exclude):
            if not isinstance(exclude, list):
                raise TypeError(f"Expected exclude to be a list, but recieved {type(exclude)}")
            for member in exclude:
                if isinstance(member, cls) and member.available:
                    member.available = False

        @staticmethod
        def __reset_availability():
            for member in

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

        def __get_selector(self):
            return (By.CSS_SELECTOR, f"input[type='checkbox'][id='{self.value}'] + span.checkbox")

        @classmethod
        def __get_full_selector_list(cls, exclude=None):
            if exclude is None:
                exclude = []
            return [column_selector.__get_selector() for column_selector in cls if column_selector not in exclude and column_selector.available]

        @classmethod
        def __get_empty_selector_list(cls, include=None):
            if include is None:
                include = []
            return [column_selector.__get_selector() for column_selector in include if isinstance(column_selector, cls) and column_selector.available]

        @classmethod
        def __get_default_map(cls):
            default_map = {}
            for member in cls:
                if member.available:
                    default_map[member] = False
            default_map[cls.MSRP] = True
            return default_map

        @classmethod
        def __get_false_map(cls):
            false_map = cls.__get_default_map()
            if cls.MSRP.available:
                false_map[cls.MSRP] = False
            return false_map

        @classmethod
        def __get_true_map(cls):
            true_map = cls.__get_false_map()
            for key in true_map:
                true_map[key] = True
            return true_map

    class Url_Paths(Enum):
        APPROACH_SHOES = "approach-shoes"
        BASKETBALL_SHOES = "basketball-shoes"
        CLIMBING_SHOES = "climbing-shoes"
        CROSSFIT_SHOES = "crossfit-shoes"
        CYCLING_SHOES = "cycling-shoes"
        FOOTBALL_CLEATS = "football-cleats"
        GOLF_SHOES = "golf-shoes"
        HIKING_BOOTS = "hiking-boots"
        HIKING_SHOES = "hiking-shoes"
        RUNNING_SHOES = "running-shoes"
        SNEAKERS = "sneakers"
        SOCCER_CLEATS = "soccer-cleats"
        TENNIS_SHOES = "tennis-shoes"
        TRACK_SHOES = "track-and-field-shoes"
        TRAINING_SHOES = "training-shoes"
        TRAIL_SHOES = "trail-running-shoes"
        WALKING_SHOES = "walking-shoes"

        class Gender(Enum):
            MEN = ()
            NONE = ()
            WOMEN = ()

        def get_url_path(self, gender=Gender.NONE):
            if gender is ScraperSingleton.Url_Paths.Gender.NONE:
                return f"/catalog/{self.value}"
            elif gender is ScraperSingleton.Url_Paths.Gender.MEN:
                return f"/catalog/mens-{self.value}"
            elif gender is ScraperSingleton.Url_Paths.Gender.WOMEN:
                return f"/catalog/womens-{self.value}"
            else:
                raise TypeError("gender must be an enumeration member of ScraperSingleton.Url_Paths.Gender")

    @classmethod
    def __setColumnSelectorAvailability(cls, url_path):
        if not isinstance(url_path, cls.Url_Paths):
            raise TypeError("url_path must be an enumeration member of ScraperSingleton.Url_Paths")
        match url_path:
            case cls.Url_Paths.APPROACH_SHOES:
                # TODO:
            case cls.Url_Paths.BASKETBALL_SHOES:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.CLOSURE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.MATERIAL,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TECHNOLOGY,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.USE,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.WIDTH,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.CLIMBING_SHOES:
                # TODO:
            case cls.Url_Paths.CROSSFIT_SHOES:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.CLOSURE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.MATERIAL,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.TECHNOLOGY,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.CYCLING_SHOES:
                # TODO:
            case cls.Url_Paths.FOOTBALL_CLEATS:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.NUMBER_OF_REVIEWS,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TECHNOLOGY,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.USE,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.ZERO_DROP
                ]
            case cls.Url_Paths.GOLF_SHOES:
                # TODO:
            case cls.Url_Paths.HIKING_BOOTS:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.HIKING_SHOES:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.RUNNING_SHOES:
                exclude_list = [
                    cls.ColumnSelector.CLOSURE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.SNEAKERS:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.USE,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.WIDTH,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.SOCCER_CLEATS:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.CLOSURE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FEATURES,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.MATERIAL,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TECHNOLOGY,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.USE,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.WIDTH,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.TENNIS_SHOES:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.CLOSURE,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.NUMBER_OF_REVIEWS,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.USE,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.TRACK_SHOES:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.MATERIAL,
                    cls.ColumnSelector.NUMBER_OF_REVIEWS,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.TECHNOLOGY,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOEBOX,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.WIDTH,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.TRAINING_SHOES:
                exclude_list = [
                    cls.ColumnSelector.ARCH_SUPPORT,
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.CLOSURE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.MATERIAL,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.TECHNOLOGY,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.TRAIL_SHOES:
                exclude_list = [
                    cls.ColumnSelector.CLOSURE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONDITION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.SURFACE,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)
            case cls.Url_Paths.WALKING_SHOES:
                exclude_list = [
                    cls.ColumnSelector.ARCH_TYPE,
                    cls.ColumnSelector.COLLABORATION,
                    cls.ColumnSelector.CONSTRUCTION,
                    cls.ColumnSelector.CUSHIONING,
                    cls.ColumnSelector.CUT,
                    cls.ColumnSelector.DESIGNED_BY,
                    cls.ColumnSelector.DISTANCE,
                    cls.ColumnSelector.EMBELLISHMENT,
                    cls.ColumnSelector.EVENT,
                    cls.ColumnSelector.FEATURE,
                    cls.ColumnSelector.FIT,
                    cls.ColumnSelector.FLEXIBILITY,
                    cls.ColumnSelector.FOOT_CONDITION,
                    cls.ColumnSelector.FOREFOOT_HEIGHT,
                    cls.ColumnSelector.GRAM_INSULATION,
                    cls.ColumnSelector.HEEL_HEIGHT,
                    cls.ColumnSelector.HEEL_TOE_DROP,
                    cls.ColumnSelector.INSPIRED_FROM,
                    cls.ColumnSelector.LACE_TYPE,
                    cls.ColumnSelector.LACING_SYSTEM,
                    cls.ColumnSelector.LOCKDOWN,
                    cls.ColumnSelector.NUMBER_OF_REVIEWS,
                    cls.ColumnSelector.ORIGIN,
                    cls.ColumnSelector.ORTHOTIC_FRIENDLY,
                    cls.ColumnSelector.PACE,
                    cls.ColumnSelector.PRICE_TIER,
                    cls.ColumnSelector.PRINT,
                    cls.ColumnSelector.PRONATION,
                    cls.ColumnSelector.PROTECTION,
                    cls.ColumnSelector.SEASON,
                    cls.ColumnSelector.SHOE_TYPE,
                    cls.ColumnSelector.SIGNATURE,
                    cls.ColumnSelector.SPIKE_SIZE,
                    cls.ColumnSelector.SPIKE_TYPE,
                    cls.ColumnSelector.STRIKE_PATTERN,
                    cls.ColumnSelector.STUD_TYPE,
                    cls.ColumnSelector.STYLE,
                    cls.ColumnSelector.SUMMER,
                    cls.ColumnSelector.SUPPORT,
                    cls.ColumnSelector.TECHNOLOGY,
                    cls.ColumnSelector.TERRAIN,
                    cls.ColumnSelector.TOP,
                    cls.ColumnSelector.TYPE,
                    cls.ColumnSelector.ULTRA_RUNNING,
                    cls.ColumnSelector.WATERPROOFING,
                    cls.ColumnSelector.WIDTH,
                    cls.ColumnSelector.ZERO_DROP
                ]
                cls.ColumnSelector.__exclude(exclude=exclude_list)

    # Set up the browser
    @classmethod
    def __initBrowser(cls):
        service = Service(cls.__driver_path)
        browser = webdriver.Chrome(service=service, options=cls.__getChromiumOptions())
        browser.delete_all_cookies()
        cls.__browser = browser

    @classmethod
    def __new__(cls):
        if platform.system() != "Linux":
            raise RuntimeError("ScraperSingleton is only intended for Linux-based OSes")
        if cls.__browser is None:
            cls.__initBrowser()
        return cls.__browser

    def __init__(self):
        pass

    # Set up Chromium options
    @classmethod
    def __getChromiumOptions(cls):
        chromium_options = Options()
        chromium_options.add_argument("--headless")
        chromium_options.add_argument("--no-sandbox")
        chromium_options.add_argument("--disable-dev-shm-usage") # /dev/shm is generally a tmpfs directory
        # Create a temporary directory for the user data
        temp_profile_dir = tempfile.mkdtemp()
        # Add the user data directory argument
        chromium_options.add_argument(f"--user-data-dir={temp_profile_dir}")
        chromium_options.binary_location = cls.__chromium_location
        return chromium_options

    @classmethod
    def __getColumnFilterDict(cls):
        if cls.__column_filter_dict is None:
            cls.__column_filter_dict = cls.ColumnSelector.__get_default_map()
        return cls.__column_filter_dict

    @classmethod
    def __setColumnFilterDict(cls, dict):
        if cls.__column_filter_dict is None:
            cls.__column_filter_dict = cls.ColumnSelector.__get_default_map()
        for key, value in dict.items():
            if isinstance(key, cls.ColumnSelector):
                if isinstance(value, bool):
                    cls.__column_filter_dict[key] = value
                else:
                    raise TypeError(f"Expected bool, but received {type(value)}")
            else:
                raise TypeError(f"Expected ScraperSingleton.ColumnSelector enumeration member, but received {type(key)}")

    # dev function to output page source
    @classmethod
    @PendingDeprecationWarning
    def __outputPageSource(cls, filename):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(cls.__browser.page_source)

    # dev function to check cookies
    @classmethod
    @PendingDeprecationWarning
    def __printCookies(cls, cookie_name=""):
        if cookie_name == "":
            PrettyPrinter(indent=4).pprint(cls.__browser.get_cookies())
        else:
            PrettyPrinter(indent=4).pprint(cls.__browser.get_cookie(cookie_name))

    @classmethod
    def __wait_and_click(cls, selector):
        element = WebDriverWait(cls.__browser, cls.__wait).until(EC.element_to_be_clickable(selector))
        element.click()

    @classmethod
    def __scroll_and_click(cls, selector):
        element = WebDriverWait(cls.__browser, cls.__wait).until(EC.presence_of_element_located(selector))
        browser.execute_script("arguments[0].click();", element)

    # Change view to table
    @classmethod
    def __getSlimListView(cls):
        cookie = cls.__browser.get_cookie("list_type")
        if cookie is None or cookie["value"] != "slim" or cookie["expiry"] < time.time():
            cls.__wait_and_click(selector=(By.CSS_SELECTOR, "svg.slim-view-icon.catalog__list-tab-icon"))

    @classmethod
    def __applyColumns(cls):
        cls.__wait_and_click(selector=(By.CSS_SELECTOR, "button.buy_now_button[data-v-795eb1ee]"))

    @classmethod
    def __editColumns(cls):
        cls.__wait_and_click(selector=(By.CSS_SELECTOR, "button.buy_now_button.edit-columns__button"))
        time.sleep(cls.__sleep)

    @classmethod
    def __getEmptyView(cls):
        cls.__editColumns()
        checkboxes = []
        for key in cls.__getColumnFilterDict():
            if cls.__getColumnFilterDict()[key]:
                checkboxes.append(key.__get_selector())
        for selector in checkboxes:
            cls.__scroll_and_click(selector=selector)
        cls.__applyColumns()
        cls.__setColumnFilterDict(cls.ColumnSelector.__get_false_map())

    @classmethod
    def __getColumnsView(cls, list):
        cls.__getEmptyView()
        cls.__editColumns()
        for item in list:
            if isinstance(item, cls.ColumnSelector):
                cls.__scroll_and_click(selector=item.__get_selector())
            else:
                raise TypeError(f"Expected ScraperSingleton.ColumnSelector enumeration member, but received {type(item)}")
        cls.__applyColumns()
        cls.__setColumnFilterDict({k: True for k in list})

    @classmethod
    def __getShoeNames(cls):
        page = 1
        shoe_names = []
        while True:
            browser.get(cls.__url + "?page=" + str(page))
            shoe_elements = cls.__browser.find_elements(By.CSS_SELECTOR, "a.catalog-list-slim__names")
            if len(shoe_elements) < 1:
                break
            for title in shoe_elements:
                shoe_names.append(title.text)
            page += 1
        return shoe_names

    @classmethod
    def __getColumnData(cls, list):
        outer_list = None
        for idx in range(len(list)):
            if not isinstance(list[idx], cls.ColumnSelector):
                raise TypeError(f"Expected ScraperSingleton.ColumnSelector enumeration member, but received {type(list[idx])}")
            page = 1
            while True:
                inner_list = []
                cls.__browser.get(cls.__url + "?page=" + str(page))
                cls.__getColumnsView([list[idx]])
                elements = browser.find_elements(By.CSS_SELECTOR, "div.catalog-list-slim__facts__column div.catalog-list-slim__shoes-fact__values span")
                if len(elements) < 1:
                    break
                for element in elements:
                    inner_list.append(element.text)
                if outer_list is None:
                    outer_list = []
                outer_list.append(inner_list)
                page += 1
        return outer_list

    @classmethod
    def __getCsvStructure(cls, list):
        shoe_names = cls.__getShoeNames()
        csv_data = []
        for name in shoe_names:
            csv_data.append({"SHOE_NAME": name})
        data_list = cls.__getColumnData(list=list)
        for inner_list in data_list:
            if len(inner_list) != len(shoe_names):
                raise ValueError(f"Incongruent Lists: names list has length {len(shoe_names)}, but a list in the data list has length {len(inner_list)}")
            idx = 0
            for item in inner_list:
                csv_data[idx][list[idx].name] = item
                idx += 1
        return csv_data

    @classmethod
    def scrape(cls, list, filename):
        if not isinstance(filename, str):
            raise TypeError("filename must be a string")
        if not re.match(r'^(/[\w\s./-]+)*\/?[\w]+\.(csv)$', filename):
            raise ValueError("filename must be a full or relative path to a csv file (existing csv files will be overwritten)")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        filedata = cls.__getCsvStructure(list)



def main():
    global browser
    initBrowser(options=getChromiumOptions())
    browser.get(url)
    getSlimListView()
    getColumnData()

    # Close the browser
    browser.quit()

if __name__ == "__main__":
    main()
