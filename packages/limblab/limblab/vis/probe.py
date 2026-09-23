import os
from typing import Any, Literal, Optional

import numpy as np
from limblab.design import theme
from limblab.models import Experiment
from limblab.utils import generate_kwargs
from vedo import Line, Plotter, Text2D, Volume, show
from vedo.pyplot import plot

CHANNEL_COLORS = ["#B0DB43", "#DB43B0", "#43B0DB", "#F2A93B", "#8E6BF2", "#F25C5C"]


def _probe(
    volume_paths: list[str],
    channel_names: list[str],
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Any | None = None,
    points=None,
):
    """Probe every selected Volume with one line and plot all intensity profiles."""

    volumes = [Volume(p) for p in volume_paths]
    colors = [CHANNEL_COLORS[i % len(CHANNEL_COLORS)] for i in range(len(volumes))]

    # Init the points
    p0, p1 = points if points is not None else ((50, 300, 400), (100, 600, 400))
    pts = Line(p0, p1, res=2).ps(4)

    # Visualize every volume as an isosurface, one colour per channel
    isosurfaces = [v.isosurface().color(c) for v, c in zip(volumes, colors)]

    # Colour legend (one label per channel)
    legend = [
        Text2D(name, pos=(0.02, 0.96 - 0.04 * i), c=c, s=1.0)
        for i, (name, c) in enumerate(zip(channel_names, colors))
    ]

    params = generate_kwargs({
        "bg": theme("palette.background"),
        "axes": 14
    })
    kwargs = generate_kwargs(params, renderer, outside_class)

    plt = Plotter(**kwargs)
    plt.show(*isosurfaces, *legend, interactive=False)

    def update_probe(vertices):
        plt.remove("figure")

        vertices = np.unique(vertices, axis=0)
        a, b = vertices
        # Probe each volume with the line and plot the intensity values
        # TODO: Make the y axis dynamic
        fig = first = None
        for i, volume in enumerate(volumes):
            pl = Line(a, b, res=25)
            pl.probe(volume)

            # Get the probed values along the line
            xvals = pl.vertices[:, 0]
            yvals = pl.pointdata[0]

            kw = dict(
                xtitle=" ",
                aspect=16 / 9,
                spline=True,
                lc=colors[i],  # line color
                marker="O",
                axes=dict(c="white", xtitle_size=0.02,),
            )
            if fig is None:
                fig = first = plot(xvals, yvals, **kw)
            else:
                fig += plot(xvals, yvals, like=first, **kw)

        fig = fig.shift(0, 25, 0).clone2d()
        fig.name = "figure"
        plt.add(fig)

    if renderer == 'pyqt':
        sptool = plt.add_spline_tool(pts, closed=True, lc='blue', pc='lightgreen', ps=30)
        sptool.add_observer(
            "end of interaction",
            lambda o, e: update_probe(sptool.spline().vertices),
        )
        plt.render()
        # don't call sptool.off() here — leave it on;
        # turn it off later from wherever your GUI signals "done probing"
        return plt

    # stand alone call, no pyqt
    sptool = plt.add_spline_tool(pts, closed=True)
    sptool.add_observer(
        "end of interaction",
        lambda o, e: update_probe(sptool.spline().vertices),
    )
    plt.interactive()   # blocks here until user presses q
    sptool.off()        # only now, after interaction is done
    return plt


def probe(
    experiment: Experiment,
    channel_names: list[str],
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
):
    names = [channel_names] if isinstance(channel_names, str) else list(channel_names)
    by_name = {c.channel_name: c for c in experiment.channels}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise ValueError(f"Channel(s) {missing} not found on this experiment.")

    # same order as the selection, so colours/legend match the plotted profiles
    volume_paths = [
        os.path.join(experiment.base, by_name[n].clean_path or by_name[n].path)
        for n in names
    ]
    return _probe(volume_paths, names, renderer, outside_class)