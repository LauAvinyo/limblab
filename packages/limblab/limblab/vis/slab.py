from typing import Any, Literal, Optional

import numpy as np
from limblab.models import Channel, Experiment
from limblab.vizutils import file2dic, styles
from vedo import (
    Axes,
    Box,
    LinearTransform,
    Mesh,
    NonLinearTransform,
    Plotter,
    Volume,
    printc,
    show,
)
import os
from limblab.utils import generate_kwargs
from limblab.design import theme


def get_stage_to_angle_dict(start_x, end_x, start_y, end_y):
    x_values = np.arange(start_x, end_x + 1).astype(int)
    y_values = np.linspace(
        start_y, end_y, num=len(x_values), dtype=int
    )  # Ensure integer y-values
    return {int(x): int(y) for x, y in zip(x_values, y_values)}


angle_d = get_stage_to_angle_dict(248, 320, 20, 40)


def _dynamic_slab(
    experiment: Experiment,
    volume_path: str,
    channel_name: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
):
    printc("Starting dynamic slab viewer...", c="y")

    # # pipeline.log (surface, stage, transformation) lives next to the volume
    # folder = os.path.dirname(volume_path)
    # pipeline_file = os.path.join(folder, "pipeline.log")
    # pipeline = file2dic(pipeline_file)
    # stage = pipeline["STAGE"]

    CMAP = "Greys"
    printc(f"Loading volume: {volume_path}", c="lg")
    vol = Volume(volume_path)  # .resize([100, 100, 100])
    printc("Volume loaded successfully", c="g")

    if experiment.transformation_matrix_path is None:
        printc("No transformation found... exit", c="r")
        exit()

    else:
        # Apply non linear tranformation
        tname = experiment.transformation_matrix_path
        
        T = LinearTransform(tname)
        # elif "morphing" in pipeline["TRANSFORMATION"]:
        #     T = NonLinearTransform(tname)

        printc("Rotation transformation loaded", c="lg")

        vol.apply_transform(T)
        vol.rotate_y(-angle_d[int(experiment.stage)])
        printc("Rotation applied to volume and limb meshes", c="g")

    # Load the limb surface
    surface = os.path.join(experiment.base, experiment.surface_path)
    limb = Mesh(surface)
    limb.color(styles["limb"]["color"]).alpha(0.1)
    limb.extract_largest_region()
    limb.apply_transform(T)
    limb.rotate_y(-angle_d[int(experiment.stage)])
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

    params: dict[str, Any] = dict(c=theme("limblab.surface"), bg = theme("palette.background"))
    kwargs = generate_kwargs(params=params, renderer=renderer, outside_class=outside_class)
    
    plt = Plotter(**kwargs) 

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

    if renderer == "pyqt":
        plt.show(axes=14, interactive=False)
        return plt

    plt.close()

    l, u = slab.metadata["slab_range"]
    slab_path = os.path.join(experiment.base, f"{channel_name}_slab_{l}_{u}.py")

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
    ).screenshot(slab_path).close()#screenshot would be nice to open a differnt window still!@


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
            channel: Channel = i

    volume_path = channel.path
    #volume_path = os.path.join(experiment.base, experiment.surface_path)
    _dynamic_slab(experiment, volume_path, channel_name, renderer, outside_class)