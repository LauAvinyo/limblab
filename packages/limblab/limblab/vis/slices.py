"""LimbLab Plotter"""

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
    qt_widget = None
):

    volume = Volume(volume_path)

    params = generate_kwargs({
        "cmaps": ("gist_ncar_r", "jet", "Spectral_r", "hot_r", "bone_r"),
        "use_slider3d": False,
        "bg": theme("palette.background"),

    })
    
    
    if __doc__ is not None:
        plt += Text2D(__doc__)

    if renderer == "pyqt":
        kwargs = generate_kwargs(params, renderer, outside_class)

        plt = Slicer3DPlotter(volume,**kwargs)

        plt.show()
        return plt

    else:
        plt = Slicer3DPlotter(volume,params)
            
        plt.show()
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
