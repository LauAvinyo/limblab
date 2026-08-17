"""LimbLab Plotter"""

from typing import Any, Literal, Optional

import numpy as np
from limblab.design import theme
from limblab.models import Channel, Experiment
from vedo import Volume, Plotter
from vedo.applications import (
    RayCastPlotter,
)

# TODO:
# This can be clean up. There are some functions no needed here.
# We can add more funtionality.
# Make a list of the functionlaity we should have.
color1 = theme("palette.channel0", "#9ce4f3")
color2 = theme("palette.channel1", "#128099")
# color1 = "#B9E9EC"
# color2 = "#1C93AE"
primary = theme("palette.primary", "#0d1b2a")
secondary = theme("palette.secondary", "#1b263b")
background = theme("palette.background", "#fb8f00")



def _raycast(
    volume_path: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
    plotter: Optional[Plotter] = None,   # <-- new parameter
):
    volume = Volume(volume_path)
    # TODO: apply transform if so.
    # transformation = pipeline.get("TRANSFORMATION", False)

    volume.mode(1).cmap("jet")  # raycasting mode

    if plotter is not None:
        # Remove only previous Volume actors (not axes or background)
        for actor in list(plotter.actors):
            if isinstance(actor, Volume):
                plotter.remove(actor)
        plotter.add(volume)
        plotter.render()         # update the Qt widget
    else:
        # Original standalone window
        plt = RayCastPlotter(volume, bg="black", axes=7)
        plt.show(viewup="z")
        plt.close()

def raycast(
    experiment: Experiment,
    channel_name: str, 
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
    plotter: Optional[Plotter] = None,   # <-- new parameter
) -> None:

    channels = experiment.channels
    channel = ""
    for i in channels:
        if i.channel_name == channel_name:
            print(i)
            channel: Channel = i 

    volume_path = channel.path
    _raycast(volume_path, renderer, outside_class, plotter=plotter)
    
