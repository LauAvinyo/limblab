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


TEST_VOLUME_PATH = Path(
    "/Users/laura/Desktop/righthindlimb3_E12_autofluorescence_488.tif"
)


experiment = Experiment(
    experiment_id="manual_test",
    base="test",
    spacing_x=1.0,
    spacing_y=1.0,
    spacing_z=1.0,
    side="R",
)


v0, v1 = pick_isovalues(TEST_VOLUME_PATH)
print(f"v0={v0}, v1={v1}")

channel = clean(
    experiment,
    TEST_VOLUME_PATH,
    "dapi",
    CleanParams(v0=v0, v1=v1),
)

print(channel)
