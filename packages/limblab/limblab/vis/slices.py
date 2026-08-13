"""LimbLab Plotter"""

from typing import Any, Literal, Optional

from limblab.models import Channel, Experiment
from vedo import Volume, Text2D
from vedo.applications import (
    Slicer3DPlotter
)
from packages.limblab.utils import file2dic, pick_evenly_distributed_values, styles
import os


def _slices(volume_path: str,
            renderer: Optional[Literal["pyqt"]] = None,
            outside_class: Optional[Any] = None):
    
    #pipeline_file = os.path.join(volume_path, "pipeline.log")
    #pipeline = file2dic(pipeline_file)
    #volume_file = os.path.join(volume_path, pipeline[channel.upper()])#what is this
    volume = Volume(volume_path)

    plt = Slicer3DPlotter(
        volume,
        cmaps=("gist_ncar_r", "jet", "Spectral_r", "hot_r", "bone_r"),
        use_slider3d=False,
        bg="white",
    )

    # Can now add any other vedo object to the Plotter scene:
    plt += Text2D(__doc__)

    plt.show(viewup="z")
    plt.close()


def slices(
    experiment: Experiment,
    channel_name: str, 
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
) -> None:

    channels = experiment.channels
    channel = ""
    for i in channels:
        if i.channel_name == channel_name:
            print(i)
            channel: Channel= i 

    volume_path = channel.path
    _slices(volume_path, channel, renderer, outside_class)
    
