import os
from typing import Any, Literal

import numpy as np
from limblab.design import theme
from limblab.models import Experiment
from limblab.utils import generate_kwargs
from vedo import Line, Plotter, Volume, show
from vedo.pyplot import plot


def _probe(
    volume_paths: list[str],
    channel_names: list[str],
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
    points=None,
):
    """Probe multiple Volumes with a line and plot the intensity values for each channel."""

    global plt

    volumes = []

    # Load each volume corresponding to the channels
    for volume_path, channel_name in zip(volume_paths, channel_names):
        volume = Volume(volume_path)
        volume.add_scalarbar3d(channel_name, c="k")
        volume.scalarbar = volume.scalarbar.clone2d("bottom-right", 0.2)
        volumes.append(volume)

    # Init the points
    LINE = True
    if points is None:
        p0 = (50, 300, 400)
        p1 = (100, 300, 400)

    if LINE:
        # Create a set of points in space
        pts = Line(p0, p1, res=2).ps(4)


    # Colors
    colors = [theme(f"palette.channel{i}") for i in range(len(volume_paths))]

    # Visualize the points and the first volume (just for visualization)
    isosurfaces = [v.isosurface() for i, v in enumerate(volumes)]
    isosurfaces = [i.color(c) for i, c in zip(isosurfaces, colors)]

    params = {}
    kwargs = generate_kwargs(params, renderer, outside_class)

    plt = Plotter(interactive=False, axes=1)
    plt.show(*isosurfaces, __doc__)

    plt = show(*isosurfaces, __doc__, interactive=False, axes=1)

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
                    marker="O",  # marker style
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
                    like=_plot,
                )

        fig = fig.shift(0, 25, 0).clone2d()
        fig.name = "figure"
        plt += fig

    # Add the spline tool using the same points and interact with it
    sptool = plt.add_spline_tool(pts, closed=True)

    # Add a callback to print the center of mass of the spline
    sptool.add_observer(
        "end of interaction",
        lambda o, e: update_probe(sptool.spline().vertices),
    )

    # Stay in the loop until the user presses q
    plt.interactive()

    # Switch off the tool
    sptool.off()

    # Extract and visualize the resulting spline
    sp = sptool.spline().lw(4)

    # pipeline.log / experiment folder lives next to the volumes
    folder = os.path.dirname(volume_paths[0])
    sp.write(os.path.join(folder, "spline.vti"))
    # show(sp, "Spline saved and ready", interactive=True, resetcam=False).close()


def probe(
    experiment: Experiment,
    channel_names: list[str],
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
    points=None,
) -> None:

    channels = experiment.channels
    volume_paths = []
    for i in channels:
        if i.channel_name in channel_names:
            volume_paths.append(i.path)

    _probe(volume_paths, channel_names, renderer, outside_class, points)