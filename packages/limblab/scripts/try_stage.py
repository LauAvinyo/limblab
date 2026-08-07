from limblab.tools.stage import stage_limb

# packages/limblab/scripts/try_clean.py
from pathlib import Path
from limblab.models import Experiment, Channel
from limblab.params import CleanParams
from limblab.tools.clean import clean, pick_isovalues

from pathlib import Path
from vedo import Volume, Plotter, Text2D
from vedo.applications import IsosurfaceBrowser

from limblab.models import Channel, Experiment
from limblab.params import CleanParams
from limblab.exceptions import VolumeProcessingError


TEST_BASE_PATH = "/Users/laura/Desktop/Desktop-2026/sox9-fig-thesis/"
TEST_SURFACE_PATH = "HCR11_MEIS2_l1_dapi_488_LF_surface.vtk"


experiment = Experiment(
    experiment_id="manual_test",
    base=TEST_BASE_PATH,
    spacing_x=1.0,
    spacing_y=1.0,
    spacing_z=1.0,
    side="F",
    position="L",
    species="mouse",
    surface=TEST_SURFACE_PATH,
)

stage_result = stage_limb(experiment)
print(f"Staging result: {stage_result}")
