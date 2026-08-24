"""
LimbLab - core library for limb development data processing and visualization.
"""

__version__ = "0.4.1"

#Database actions
from .database.crud import (
    delete_experiment,
    get_engine,
    init_db,
    save_experiment,
    update_experiment,
    delete_channel,
    rename_experiment
)

from .database.navigation import (
    delete_from_database_going_back_action,
    seed_reference_limbs
)

#Design logistics
from .design import DESIGN_TOKENS, get_design_token, theme

#Limb processing tools
from .tools.align import _store_transformation_matrix, rotate_limb
from .tools.clean import clean, get_channel_path, pick_isovalues
from .tools.show_tiff import preview_volume
from .tools.stage import stage_limb_embedded
from .tools.surface import (
    auto_isovalue,
    extract_surface,
    get_nuclei_channel_path,
    pick_isovalue,
)

#Visualizations
from .vis.isosurface import (two_chanel_isosurface, one_channel_isosurface)
from .vis.probe import probe
from .vis.raycast import raycast
from .vis.slices import slices
from .vis.slab import dynamic_slab


from .vizutils import file2dic, pick_evenly_distributed_values, styles

__all__ = [
    "_store_transformation_matrix",
    "auto_isovalue",
    "clean",
    # "create_test_database",
    "delete_experiment",
    "extract_surface",
    # database functions
    "get_engine",
    # "get_experiment",
    "init_db",
    # "list_experiment",
    "pick_isovalue",
    "pick_isovalues",
    "rotate_limb",
    "save_experiment",
    "stage_limb",
    "update_experiment",
    "get_nuclei_channel_path", 
    'pick_isovalues',
    'clean',
    'get_channel_path',
    'check_connection',
    '_stage_connection',
    'stage_limb_embedded',
    'preview_volume',
    'delete_channel',
    'rename_experiment',
    'one_channel_isosurface',
    'two_chanel_isosurface',
    'dynamic_slab',
    'probe',
    'raycast',
    'slices',
    'file2dic',
    'pick_evenly_distributed_values',
    'styles',
    'seed_reference_limbs',
    'delete_from_database_going_back_action'
    
]
#les funcions privades s-haurien de poder ficar aqui????