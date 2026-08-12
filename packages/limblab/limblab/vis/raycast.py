"""LimbLab Plotter"""

from typing import Any, Literal, Optional

import numpy as np
from limblab.models import Channel, Experiment
from vedo import Volume
from vedo.applications import (
    RayCastPlotter,
)

# TODO:
# This can be clean up. There are some functions no needed here.
# We can add more funtionality.
# Make a list of the functionlaity we should have.
color1 = "#9ce4f3"
color2 = "#128099"
# color1 = "#B9E9EC"
# color2 = "#1C93AE"
primary = "#0d1b2a"
secondary = "#1b263b"
background = "#fb8f00"



def _raycast(    
    volume_path: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
):

    volume = Volume(volume_path)
    # TODO: apply transform if so.
    # transformation = pipeline.get("TRANSFORMATION", False)

    volume.mode(1).cmap("jet")  # type: ignore # change visual properties

    # Create a Plotter instance and show
    plt = RayCastPlotter(volume, bg="white", axes=7)
    plt.show(viewup="z")
    plt.close()

def raycast(
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
            channel: Channel = i 

    volume_path = channel.path
    _raycast(volume_path, renderer, outside_class)
    
