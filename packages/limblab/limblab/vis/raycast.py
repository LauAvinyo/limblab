"""LimbLab Plotter"""

from typing import Any, Literal, Optional

import numpy as np
from limblab.design import theme
from limblab.models import Channel, Experiment
from vedo import Volume, Plotter
from vedo.applications import (
    RayCastPlotter,
)
import os

from limblab.utils import generate_kwargs

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


#function call from controller -> raycast(self.experiment, channel_name=channel.channel_name, plotter=plotter)
def _raycast(
    volume_path: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
    ):  

    volume = Volume(volume_path)

    volume.mode(1).cmap("jet")  # raycasting mode

    if renderer == 'pyqt':

        params = generate_kwargs({'bg': theme('palette.background'), 'axes': 7})
        kwargs = generate_kwargs(params, renderer, outside_class)

        plt = RayCastPlotter(volume, **kwargs)

        plt.show()
        return plt   

    
    else:  
        params = generate_kwargs({'bg': theme('palette.background'), 'axes': 7})
        kwargs = generate_kwargs(params)
        
        plt = RayCastPlotter(volume, **kwargs)
       
        plt.show()
        plt.close()

def raycast(
    experiment: Experiment,
    channel_name: str, 
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
) -> None: 

    channel = next((c for c in experiment.channels if c.channel_name == channel_name), None)
    if channel is None:
        raise ValueError(f"No channel named '{channel_name}' found on this experiment.")

    if not channel.clean_path:
        raise ValueError(f"Channel '{channel_name}' has no clean_path — clean it before visualizing.")

    volume_path = os.path.join(experiment.base, channel.clean_path)
    _raycast(volume_path, renderer, outside_class)

