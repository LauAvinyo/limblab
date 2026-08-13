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
    Box,
    Axes
)
from vedo.applications import (
    Slicer3DPlotter
)
from packages.limblab.utils import file2dic, pick_evenly_distributed_values, styles
import os
from vedo.pyplot import plot


def _dynamic_slab(    
    volume_path: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
):
    printc("Starting dynamic slab viewer...", c="y")
    #pipeline_file = os.path.join(folder, "pipeline.log")
    #pipeline = file2dic(pipeline_file)
    #surface = pipeline["SURFACE"]
    #stage = pipeline["STAGE"]

    CMAP = "Greys"
    printc(f"Loading volume: {volume_path}", c="lg")
    vol = Volume(volume_path)  # .resize([100, 100, 100])
    printc("Volume loaded successfully", c="g")

    # Apply non linear tranformation
    #tname = os.path.join(folder, pipeline["TRANSFORMATION"])
    if "rotation" in pipeline["TRANSFORMATION"]:
        T = LinearTransform(tname)
    elif "morphing" in pipeline["TRANSFORMATION"]:
        T = NonLinearTransform(tname)
    else:
        printc("No transformation found... exit", c="r")
        exit()

    # tname = os.path.join(folder, pipeline["ROTATION"])
    # T = LinearTransform(tname)
    printc("Rotation transformation loaded", c="lg")

    vol.apply_transform(T)
    vol.rotate_y(-angle_d[int(stage)])
    printc("Rotation applied to volume and limb meshes", c="g")

    # Load the limb surface
    surface = os.path.join(folder, pipeline.get("BLENDER", pipeline["SURFACE"]))

    limb = Mesh(surface)
    limb.color(styles["limb"]["color"]).alpha(0.1)
    limb.extract_largest_region()
    limb.apply_transform(T)
    limb.rotate_y(-angle_d[int(stage)])
    vaxes = Axes(
        vol,
        xygrid=False,
    )  # htitle=volume.replace("_", "-")
    printc("Limb surface loaded and transformed", c="g")
    # Box
    global slab, slab_box, box_limits

    # TODO: Get a better min/max for slab range
    box_vmin = 0
    box_vmax = 1000
    box_min = box_vmin
    box_max = box_vmax
    box_limits = [box_min, box_max]
    slab = vol.slab(box_limits, axis="z", operation="mean")
    bbox = slab.metadata["slab_bounding_box"]
    zslab = slab.zbounds()[0] + 1000
    slab.z(-zslab)  # move slab to the bottom  # move slab to the bottom
    slab_box = Box(bbox).wireframe().c("black")
    slab.cmap(CMAP)  # .add_scalarbar("slab")

    def slider1(widget, event):
        global slab, slab_box, box_limits

        box_limits[0] = int(widget.value)
        plt.remove(slab)
        plt.remove(slab_box)
        slab = vol.slab(box_limits, axis="z", operation="mean")
        bbox = slab.metadata["slab_bounding_box"]
        zslab = slab.zbounds()[0] + 1000
        slab.z(-zslab)  # move slab to the bottom
        slab_box = Box(bbox).wireframe().c("black")
        slab.cmap(CMAP)  # .add_scalarbar("slab")
        plt.add(slab)
        plt.add(slab_box)

    def slider2(widget, event):
        global slab, slab_box, box_limits

        new_value = int(widget.value)

        # if new_value <= box_limits[0]:
        #     return

        box_limits[1] = new_value
        plt.remove(slab)
        plt.remove(slab_box)
        slab = vol.slab(box_limits, axis="z", operation="mean")
        bbox = slab.metadata["slab_bounding_box"]
        zslab = slab.zbounds()[0] + 1000
        slab.z(-zslab)  # move slab to the bottom
        slab_box = Box(bbox).wireframe().c("black")
        slab.cmap(CMAP)  # .add_scalarbar("slab")
        plt.add(slab)
        plt.add(slab_box)

    limb_clone = limb.clone()
    limb_clone.project_on_plane()
    # limb_clone.z(slab.z() - 360)
    printc("Ready to display the scene", c="y")
    # exit()
    plt = Plotter()

    plt += vol.isosurface()
    plt += limb
    # plt += limb_clone.color("black").alpha(0.01)
    plt += slab
    plt += slab_box
    plt += vaxes

    plt.add_slider(
        slider1,
        xmin=box_vmin,
        xmax=box_vmax,
        value=box_vmin,
        c=styles["ui"]["primary"],
        pos="bottom-left",  # type: ignore
        title="Slab Min Value",
    )

    plt.add_slider(
        slider2,
        xmin=box_vmin,
        xmax=box_vmax,
        value=box_vmax,
        c=styles["ui"]["primary"],
        pos="bottom-right",  # type: ignore
        title="Slab Max Value",
    )

    plt.show(axes=14, zoom=1.5).close()

    l, u = slab.metadata["slab_range"]
    slab_path = os.path.join(folder, f"{channel}_slab_{l}_{u}.py")

    show(
        slab,
        #  limb_clone.silhouette(top_camera_slab, border_edges=False),
        # camera=dict(
        #     pos=(781.020, 70.1935, 2107.68),
        #     focal_point=(781.020, 70.1935, 33.6000),
        #     viewup=(-2.46519e-32, 1.00000, 0),
        #     roll=-1.41245e-30,
        #     distance=2074.08,
        #     clipping_range=(2904.91, 3356.75),
        # )
    ).screenshot(slab_path).close()


def dynamic_slab(
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
            channel: Channel= i 

    volume_path = channel.path
    _dynamic_slab(volume_path, renderer, outside_class)