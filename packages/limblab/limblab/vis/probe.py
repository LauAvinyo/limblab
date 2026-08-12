from typing import Any, Literal, Optional

from limblab.models import Channel, Experiment
from vedo import (
    Line,
    LinearTransform,
    Mesh,
    NonLinearTransform,
    PlaneCutter,
    Plotter,
    Text2D,
    Volume,
    printc,
    show,
)

from packages.limblab.utils import file2dic, pick_evenly_distributed_values, styles
import os
from vedo.pyplot import plot
import numpy as np

def _probe(folder, channels, points=None):
    """Probe multiple Volumes with a line and plot the intensity values for each channel."""

    global plt, fig

    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    volumes = []

    # Load each volume corresponding to the channels
    for channel in channels:
        volume_file = os.path.join(folder, pipeline[channel.upper()])
        volume = Volume(volume_file)
        volume.add_scalarbar3d(channel, c="k")
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
    colors = [styles[f"channel_{i}"]["color"] for i in range(len(channels))]

    # Visualize the points and the first volume (just for visualization)
    isosurfaces = [v.isosurface() for i, v in enumerate(volumes)]
    isosurfaces = [i.color(c) for i, c in zip(isosurfaces, colors)]
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
    sp.write(os.path.join(folder, "spline.vti"))
    # show(sp, "Spline saved and ready", interactive=True, resetcam=False).close()


#TODO this needs updating, non matching arguments
def probe(folder, channel, points=None):
    """Probe a Volume with a line and plot the intensity values"""

    global plt, fig

    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    volume_file = os.path.join(folder, pipeline[channel.upper()])
    volume = Volume(volume_file)
    volume.add_scalarbar3d(channel, c="k")
    volume.scalarbar = volume.scalarbar.clone2d("bottom-right", 0.2)

    # Init the points
    LINE = True
    if points is None:
        p0 = (50, 300, 400)
        p1 = (100, 300, 400)

    if LINE:
        # Create a set of points in space
        pts = Line(p0, p1).ps(4)

    # Visualize the points
    plt = show(pts, volume.isosurface(), __doc__, interactive=False, axes=1)

    def update_probe(vertices):
        global plt

        plt.remove("figure")

        vertices = np.unique(vertices, axis=0)
        printc(f"Probe points: {vertices}", c="lg")
        p0, p1 = vertices
        # Probe the Volume with the line
        pl = Line(p0, p1, res=100)
        pl.probe(volume)

        # Get the probed values along the line
        xvals = pl.vertices[:, 0]
        yvals = pl.pointdata[0]

        # Plot the intensity values
        fig = plot(
            xvals,
            yvals,
            xtitle=" ",
            ytitle="voxel intensity",
            aspect=16 / 9,
            spline=True,
            lc="r",  # line color
            marker="O",  # marker style
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
    sp.write(os.path.join(folder, "spline.vti"))
    show(sp, "Spline saved and ready for use", interactive=True, resetcam=False).close()
