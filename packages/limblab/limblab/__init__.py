"""
LimbLab - core library for limb development data processing and visualization.
"""

__version__ = "0.4.1"

from .tools.clean import clean, pick_isovalues
from .tools.surface import extract_surface, auto_isovalue, pick_isovalue
from .tools.stage import stage_limb 
from .tools.align import rotate_limb
from .database import get_engine, init_db, save_experiment, update_experiment, delete_experiment
# add other tools as you migrate them:
# from .tools.rotate import rotate

from .exceptions import LimbLabError, VolumeProcessingError

__all__ = [
    "clean",
    "pick_isovalues",
    "auto_isovalue",
    "pick_isovalue",
    "extract_surface",
    "stage_limb",
    "rotate_limb",
    "LimbLabError",
    "VolumeProcessingError",

    # database functions
    "get_engine",
    "init_db",
    "update_experiment",

]