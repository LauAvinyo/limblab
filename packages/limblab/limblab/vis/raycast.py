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
    plotter: Optional[Plotter] = None,
    qt_widget=None
    ):   # <-- new parameter

    volume = Volume(volume_path)
    # TODO: apply transform if so.
    # transformation = pipeline.get("TRANSFORMATION", False)

    volume.mode(1).cmap("jet")  # raycasting mode

    if qt_widget is not None:
        plt = RayCastPlotter(volume, bg="black", axes=7, qt_widget=qt_widget)
        plt.show()
        return plt   # caller must keep a reference so it isn't GC'd
    else:
        plt = RayCastPlotter(volume, bg="black", axes=7)
        plt.show()
        plt.close()

def raycast(
    experiment: Experiment,
    channel_name: str, 
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
    plotter: Optional[Plotter] = None,
    qt_widget=None,
) -> None:

    channel = next((c for c in experiment.channels if c.channel_name == channel_name), None)
    if channel is None:
        raise ValueError(f"No channel named '{channel_name}' found on this experiment.")

    if not channel.clean_path:
        raise ValueError(f"Channel '{channel_name}' has no clean_path — clean it before visualizing.")

    volume_path = os.path.join(experiment.base, channel.clean_path)
    _raycast(volume_path, renderer, outside_class, plotter=plotter, qt_widget=qt_widget)

''''    TESTING!
TEST_SURFACE_PATH = "HCR12_HOXA11_l1_dapi_405_LF_surface.vtk"
TEST_DAPI_FILENAME = "HCR12_HOXA11_l1_dapi_405_LF.vti" 
TEST_BASE_PATH = 'C:\\Users\\millan\\Desktop\\prova'
REFERENCE_LIMB_FOLDER = 'C:\\Users\\millan\\Desktop\\limblab\\packages\\limblab\\limblab\\limb'


if __name__ == "__main__":
    experiment = Experiment(
    experiment_id="manual_test",
    base=TEST_BASE_PATH,
    spacing_x=1.0,
    spacing_y=1.0,
    spacing_z=1.0,
    side="F",
    position="L",
    species="mouse",
    surface_path=TEST_SURFACE_PATH,
    surface_isovalue=165,
    stage=260,
    channels=[
        Channel(
            experiment_id="manual_test",
            channel_name="DAPI",
            path=TEST_DAPI_FILENAME,
            clean_path = "C:\\Users\\millan\\Desktop\\HOXA11\\HCR11_HOXA11_l1_dapi_488_LH.vti",
            clean_isovalue_min = 0,
            clean_isovalue_max = 54,
            
        )
    ],
)

    raycast(experiment, 'DAPI')

'''