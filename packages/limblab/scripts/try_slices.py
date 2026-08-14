# packages/limblab/scripts/try_clean.py
from pathlib import Path

from limblab.models import Channel, Experiment
from limblab.vis.slices import slices

TEST_VOLUME_PATH = Path(
    "/Users/laura/Desktop/Desktop-2026/sox9-fig-thesis/HCR11_MEIS2_l1_sox9_594_LF.vti"
)


EXPERIMENT_ID = "manual_test"

channel = Channel(
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
    channels=[channel],
)


slices(experiment, "Sox9")
