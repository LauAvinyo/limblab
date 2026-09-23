"""LimbLab Plotter"""

import os
from typing import Any, Literal, Optional

from limblab.models import Channel, Experiment
from limblab.utils import generate_kwargs
from vedo import Text2D, Volume
from vedo.applications import Slicer3DPlotter
from limblab.design import theme


def _slices(
    volume_path: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] | None = None,
    qt_widget=None,
):
    volume = Volume(volume_path)

    params = generate_kwargs({
        "cmaps": ("gist_ncar_r", "jet", "Spectral_r", "hot_r", "bone_r"),
        "use_slider3d": False,
        "bg": theme("palette.background"),
    })

    if renderer == "pyqt":
        kwargs = generate_kwargs(params, renderer, outside_class)
        plt = Slicer3DPlotter(volume, **kwargs)
        if __doc__ is not None:
            plt += Text2D(__doc__)      # was used before `plt` existed
        plt.show()
        return plt

    plt = Slicer3DPlotter(volume, **params)   # was passed positionally as a dict
    if __doc__ is not None:
        plt += Text2D(__doc__)
    plt.show()
    plt.close()
    return None


def slices(
    experiment: Experiment,
    channel_names: list[str] | str,
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
):
    """Slicer3DPlotter only handles ONE volume, so with several channels the
    first one is shown (this mode isn't in the controller's MODES list)."""
    names = [channel_names] if isinstance(channel_names, str) else list(channel_names)
    by_name = {c.channel_name: c for c in experiment.channels}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise ValueError(f"Channel(s) {missing} not found on this experiment.")

    channel: Channel = by_name[names[0]]
    volume_path = os.path.join(experiment.base, channel.clean_path or channel.path)
    return _slices(volume_path, renderer, outside_class)