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

CHANNEL_COLORS = ["#B0DB43", "#DB43B0", "#43B0DB", "#F2A93B", "#8E6BF2", "#F25C5C"]

#function call from controller -> raycast(self.experiment, channel_name=channel.channel_name, plotter=plotter)
MULTI_MODE = 1   # 0 composite, 1 max-intensity, 4 additive ... try 0 or 4 if overlaps look odd


def _raycast(volume_paths, channel_names, renderer=None, outside_class=None):
    params = generate_kwargs({'bg': theme('palette.background'), 'axes': 7})
    if renderer == 'pyqt':
        kwargs = generate_kwargs(params, renderer, outside_class)
    else:
        kwargs = generate_kwargs(params)

    # ---- single channel: unchanged behaviour ----
    if len(volume_paths) == 1:
        volume = Volume(volume_paths[0])
        volume.mode(1).cmap("jet")
        plt = RayCastPlotter(volume, **kwargs)
        plt.show()
        if renderer == 'pyqt':
            return plt
        plt.close()
        return None

    # ---- several channels: one volume per channel in the same scene ----
    plt = Plotter(**kwargs)
    for k, (path, name) in enumerate(zip(volume_paths, channel_names)):
        color = CHANNEL_COLORS[k % len(CHANNEL_COLORS)]        
        vol = Volume(path)
        vol.mode(MULTI_MODE)
        vol.cmap(["black", color]).alpha([0.0, 0.3, 0.9])
        vol.name = name
        plt.add(vol)

        def make_cb(v):
            def cb(widget, event):
                v.alpha_unit(float(widget.value))   # higher = more transparent
            return cb

        y = 0.05 + 0.07 * k
        plt.add_slider(make_cb(vol), xmin=0.1, xmax=10, value=1,
                       pos=([0.05, y], [0.3, y]), c=color,
                       title=f"{name}: transparency")

    plt.show()
    if renderer == 'pyqt':
        return plt
    plt.close()
    return None


def raycast(experiment: Experiment, channel_names, renderer=None, outside_class=None):
    names = [channel_names] if isinstance(channel_names, str) else list(channel_names)
    by_name = {c.channel_name: c for c in experiment.channels}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise ValueError(f"Channel(s) {missing} not found on this experiment.")

    paths = []
    for n in names:
        ch = by_name[n]
        if not ch.clean_path:
            raise ValueError(f"Channel '{n}' has no clean_path — clean it before visualizing.")
        paths.append(os.path.join(experiment.base, ch.clean_path))
    return _raycast(paths, names, renderer, outside_class)