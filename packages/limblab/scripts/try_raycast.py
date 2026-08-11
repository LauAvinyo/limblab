# packages/limblab/scripts/try_clean.py
from pathlib import Path

from limblab.models import Channel, Experiment
from limblab.vis.raycast import raycast

TEST_VOLUME_PATH = Path(
    "/Users/laura/Desktop/righthindlimb3_E12_autofluorescence_488.tif"
)
EXPERIMENT_ID = "manual_test"

nuclei_channel = Channel(
    experiment_id=EXPERIMENT_ID,
    channel_name="Sox9",
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


raycast(experiment, "Sox9")
