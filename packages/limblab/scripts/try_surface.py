# packages/limblab/scripts/try_clean.py
from pathlib import Path
from limblab.models import Experiment, Channel
from limblab.params import CleanParams

from pathlib import Path
from vedo import Volume, Plotter, Text2D
from vedo.applications import IsosurfaceBrowser

from limblab.models import Channel, Experiment
from limblab.params import CleanParams
from limblab.exceptions import VolumeProcessingError
from limblab.tools.surface import pick_isovalue, auto_isovalue, extract_surface

TEST_VOLUME_PATH = Path(
    "/Users/laura/Desktop/righthindlimb3_E12_autofluorescence_488.tif"
)
EXPERIMENT_ID = "manual_test"

nuclei_channel = Channel(
    experiment_id=EXPERIMENT_ID,
    channel_name="nuclei",
    path=str(TEST_VOLUME_PATH),
    v0=0.0,
    v1=0.0,
)

experiment = Experiment(
    experiment_id=EXPERIMENT_ID,
    base="test",
    spacing_x=1.0,
    spacing_y=1.0,
    spacing_z=1.0,
    side="R",
    channels=[nuclei_channel],
)


# v  = pick_isovalue(TEST_VOLUME_PATH)
# print(f"v={v}")

v = auto_isovalue(TEST_VOLUME_PATH)
print(f"v={v}")

print("Extracting surface...")

surface_path = extract_surface(experiment, isovalue=v)
print(f"Surface extracted to: {surface_path}")
# v=740.78
