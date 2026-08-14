"""LimbLab Plotter"""

from typing import Any, Literal

from limblab.models import Channel, Experiment
from limblab.utils import generate_kwargs
from vedo import Text2D, Volume
from vedo.applications import Slicer3DPlotter


def _slices(
    volume_path: str,
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
):

    volume = Volume(volume_path)

    params: dict[str, Any] = {
        "cmaps": ("gist_ncar_r", "jet", "Spectral_r", "hot_r", "bone_r"),
        "use_slider3d": False,
        "bg": "white",
    }

    kwargs = generate_kwargs(
        params=params, renderer=renderer, outside_class=outside_class
    )

    plt = Slicer3DPlotter(
        volume,
        **kwargs
    )

    if __doc__ is not None:
        plt += Text2D(__doc__)

    if renderer == "pyqt":
        plt.show(viewup="z", interactive=False)
        return plt

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
            channel: Channel = i

    volume_path = channel.path
    _slices(volume_path, renderer, outside_class)
