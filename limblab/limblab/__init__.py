"""
LimbLab - A comprehensive library for limb development data processing and visualization.

This package provides a complete pipeline for analyzing limb development data:

Core Functions:
    - create_experiment: Initialize experiment structure
    - clean_volume: Preprocess and clean volume data
    - extract_surface: Create 3D surface meshes
    - stage_limb: Determine limb developmental stage
    - rotate_limb: Align limb with reference template
    - morph_limb: Non-linear morphing for precise alignment

Visualization:
    - one_channel_isosurface: Single channel 3D rendering
    - two_chanel_isosurface: Dual channel 3D rendering
    - raycast: Volume raycasting visualization
    - slices: 2D slice visualization
    - dynamic_slab: Interactive slab visualization
    - probe: Interactive probe visualization

Utilities:
    - load_pipeline: Load experiment pipeline data
    - file2dic/dic2file: File format conversion
    - get_reference_limb: Access reference templates

Usage:
    >>> import limblab
    >>> limblab.create_experiment("./experiment", "my_experiment")
    >>> limblab.clean_volume("./experiment", "raw_data.tif", "DAPI")
    >>> limblab.extract_surface("./experiment", auto=True)

For command-line usage, see: limblab --help
"""

__version__ = "0.3.0"

# Core pipeline functions
from .pipeline import _create_experiment as create_experiment

# Volume processing tools
from .tools import (
    _clean_volume as clean_volume,
    _extract_surface as extract_surface,
    _stage_limb as stage_limb,
    _rotate_limb as rotate_limb,
    _morph_limb as morph_limb,
)

# Visualization functions
from .visualizations import (
    one_channel_isosurface,
    two_chanel_isosurface,
    dynamic_slab,
    probe,
    raycast,
    slices,
    arbitary_slice,
)

# Utility functions
from .utils import (
    load_pipeline,
    file2dic,
    dic2file,
    closest_value,
    get_reference_limb,
    interpolate_colors,
    pick_evenly_distributed_values,
)

# Constants
from .constants import (
    VOLUME_EXTENSION,
    SURFACE_EXTENSION,
    PIPELINE_LOG_FILE,
    DEFAULT_VOLUME_SPACING,
    DEFAULT_GAUSSIAN_SIGMA,
    DEFAULT_FREQUENCY_CUTOFF,
    DEFAULT_LOW_RES_SIZE,
    VALID_LIMB_SIDES,
    VALID_LIMB_POSITIONS,
    EXPERIMENT_FOLDER_HELP,
)



# Main CLI app
from .main import app

__all__ = [
    # Core functions
    "create_experiment",
    "clean_volume",
    "extract_surface",
    "stage_limb",
    "rotate_limb",
    "morph_limb",
    # Visualizations
    "one_channel_isosurface",
    "two_chanel_isosurface",
    "dynamic_slab",
    "probe",
    "raycast",
    "slices",
    "arbitary_slice",
    # Utilities
    "load_pipeline",
    "file2dic",
    "dic2file",
    "closest_value",
    "get_reference_limb",
    "interpolate_colors",
    "pick_evenly_distributed_values",
    # Constants
    "VOLUME_EXTENSION",
    "SURFACE_EXTENSION",
    "PIPELINE_LOG_FILE",
    "DEFAULT_VOLUME_SPACING",
    "DEFAULT_GAUSSIAN_SIGMA",
    "DEFAULT_FREQUENCY_CUTOFF",
    "DEFAULT_LOW_RES_SIZE",
    "VALID_LIMB_SIDES",
    "VALID_LIMB_POSITIONS",
    "EXPERIMENT_FOLDER_HELP",
    # CLI
    "app",
]
