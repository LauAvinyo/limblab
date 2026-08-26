import os
from typing import Any, Literal, Optional

import numpy as np
from limblab.design import theme
from limblab.models import Experiment
from limblab.utils import generate_kwargs
from vedo import Line, Plotter, Volume, show
from vedo.pyplot import plot


def _probe(
    volume_paths: list[str],
    channel_names: list[str],
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Any | None = None,
    points=None,
):
    """Probe multiple Volumes with a line and plot the intensity values for each channel."""

    global plt, fig

    volumes = []


    volume = Volume(volume_paths[0])
    volume.add_scalarbar3d(channel_names, c="k")
    volume.scalarbar = volume.scalarbar.clone2d("bottom-right", 0.2)
    volumes.append(volume)

    # Init the points
    LINE = True
    if points is None:
        p0 = (50, 300, 400)
        p1 = (100, 600, 400)

    if LINE:
        # Create a set of points in space
        pts = Line(p0, p1, res=2).ps(4)

    # Colors
    colors = ["cyan", "yellow", "green"]

    # Visualize the points and the first volume (just for visualization)
    isosurfaces = [v.isosurface() for i, v in enumerate(volumes)]
    isosurfaces = [i.color(c) for i, c in zip(isosurfaces, colors)]

    params = generate_kwargs({
        "bg": theme("palette.background"), 
        "axes": 14
    })
    kwargs = generate_kwargs(params, renderer, outside_class)

    plt = Plotter(**kwargs)
    # plt += pts
    plt.show(*isosurfaces, __doc__, interactive=False)

    def update_probe(vertices):
        global plt

        plt.remove("figure")

        vertices = np.unique(vertices, axis=0)
        p0, p1 = vertices
        # Probe each volume with the line and plot the intensity values
        # TODO: Make the y axis dynamic
        for i, volume in enumerate(volumes):
            pl = Line(p0, p1, res=25)
            pl.probe(volume)

            # Get the probed values along the line
            xvals = pl.vertices[:, 0]
            yvals = pl.pointdata[0]

            if i == 0:
                _plot = plot(
                    xvals,
                    yvals,
                    xtitle=" ",
                    aspect=16 / 9,
                    spline=True,
                    lc=colors[i],  # line color
                    marker="O",
                    axes=dict(c="white", xtitle_size=0.02,),
                )
                fig = _plot
            else:
                fig += plot(
                    xvals,
                    yvals,
                    xtitle=" ",
                    aspect=16 / 9,
                    spline=True,
                    lc=colors[i],  # line color
                    marker="O",  # marker style
                    axes=dict(c="white", xtitle_size=0.02,),
                    like=_plot,
                )

        fig = fig.shift(0, 25, 0).clone2d()
        fig.name = "figure"
        plt += fig

    if renderer == 'pyqt':
        sptool = plt.add_spline_tool(pts, closed=True, lc = 'blue', pc = 'lightgreen' , ps = 30)
        sptool.add_observer(
                "end of interaction",
                lambda o, e: update_probe(sptool.spline().vertices),
            )
        plt.render()        
    # don't call sptool.off() here — leave it on;
    # turn it off later from wherever your GUI signals "done probing"

    else:
        #stand alone call, no pyqt
        sptool = plt.add_spline_tool(pts, closed=True)
        sptool.add_observer(
            "end of interaction",
            lambda o, e: update_probe(sptool.spline().vertices),
        )
        plt.interactive()   # blocks here until user presses q
        sptool.off()         # only now, after interaction is done


def probe(
    experiment: Experiment,
    channel_names: list[str],
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
) -> None: 

    channels = experiment.channels
    volume_paths = []
    for i in channels:
        if i.channel_name in channel_names:
            volume_paths.append(i.path)

    _probe(volume_paths, channel_names, renderer, outside_class)
    #points = None