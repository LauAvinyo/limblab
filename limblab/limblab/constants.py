"""
Constants used throughout the LimbLab library.

This module contains constants that are used in multiple places
to make the code easier to maintain.
"""

# File extensions
VOLUME_EXTENSION = ".vti"
SURFACE_EXTENSION = ".vtk"
PIPELINE_LOG_FILE = "pipeline.log"

# Default values
DEFAULT_VOLUME_SPACING = (0.65, 0.65, 2.0)
DEFAULT_GAUSSIAN_SIGMA = (6, 6, 6)
DEFAULT_FREQUENCY_CUTOFF = 0.05
DEFAULT_LOW_RES_SIZE = (512, 512, 296)

# Validation values
VALID_LIMB_SIDES = ["R", "L"]
VALID_LIMB_POSITIONS = ["H", "F"]

# Messages
EXPERIMENT_FOLDER_HELP = "Path to the experiment folder" 