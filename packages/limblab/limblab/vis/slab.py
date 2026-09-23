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

CHANNEL_COLORS = ["#B0DB43", "#DB43B0", "#43B0DB", "#F2A93B", "#8E6BF2", "#F25C5C"]
LAYER_GAP = 30   # z distance between the slabs of different channels


def get_stage_to_angle_dict(start_x, end_x, start_y, end_y):
    x_values = np.arange(start_x, end_x + 1).astype(int)
    y_values = np.linspace(
        start_y, end_y, num=len(x_values), dtype=int
    )  # Ensure integer y-values
    return {int(x): int(y) for x, y in zip(x_values, y_values)}


angle_d = get_stage_to_angle_dict(248, 320, 20, 40)


def _dynamic_slab(
    experiment: Experiment,
    volumes_info: list[tuple[str, str]],     # [(channel_name, volume_path), ...]
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
):
    printc("Starting dynamic slab viewer...", c="y")
    CMAP = "Greys"
    multi = len(volumes_info) > 1

    if experiment.transformation_matrix_path is None:
        # raise instead of exit(): exit() would close the whole GUI
        raise ValueError("No transformation found — align the experiment before using Slab.")
    T = LinearTransform(os.path.join(experiment.base, experiment.transformation_matrix_path))
    angle = -angle_d[int(experiment.stage)]

    vols = []
    for name, path in volumes_info:
        printc(f"Loading volume: {path}", c="lg")
        vol = Volume(path)
        vol.apply_transform(T)
        vol.rotate_y(angle)
        vols.append(vol)
    printc("Volumes loaded and transformed", c="g")

    # Load the limb surface
    limb = Mesh(os.path.join(experiment.base, experiment.surface_path))
    limb.c(theme('limblab.surface')).alpha(0.1)
    limb.extract_largest_region()
    limb.apply_transform(T)
    limb.rotate_y(angle)
    vaxes = Axes(vols[0], xygrid=False)
    printc("Limb surface loaded and transformed", c="g")

    # TODO: Get a better min/max for slab range
    box_vmin, box_vmax = 0, 1000
    limits = [box_vmin, box_vmax]
    state = {"slabs": [], "box": None}

    params = generate_kwargs({"bg": theme("palette.background"), "axes": 14})
    kwargs = generate_kwargs(params, renderer, outside_class)
    plt = Plotter(**kwargs)

    def build():
        for s in state["slabs"]:
            plt.remove(s)
        if state["box"] is not None:
            plt.remove(state["box"])

        slabs, bbox = [], None
        for k, vol in enumerate(vols):
            s = vol.slab(limits, axis="z", operation="mean")
            if bbox is None:
                bbox = s.metadata["slab_bounding_box"]
            zslab = s.zbounds()[0] + 1000
            s.z(-zslab - k * LAYER_GAP)          # each channel on its own layer
            if multi:
                s.cmap(["black", CHANNEL_COLORS[k % len(CHANNEL_COLORS)]])
            else:
                s.cmap(CMAP)
            slabs.append(s)

        state["slabs"] = slabs
        state["box"] = Box(bbox).c("dodgerblue").alpha(0.15).lw(2).lc("white")
        for s in slabs:
            plt.add(s)
        plt.add(state["box"])

    for k, vol in enumerate(vols):
        iso = vol.isosurface()
        if multi:
            iso.color(CHANNEL_COLORS[k % len(CHANNEL_COLORS)]).alpha(0.4)
        plt += iso
    plt += limb
    build()
    plt += vaxes

    def make_slider(idx):
        def cb(widget, event):
            limits[idx] = int(widget.value)
            build()
        return cb

    plt.add_slider(
        make_slider(0),
        xmin=box_vmin,
        xmax=box_vmax,
        value=box_vmin,
        c=theme('palette.primary'),
        pos="bottom-left",  # type: ignore
        title="Slab Min Value",
    )

    plt.add_slider(
        make_slider(1),
        xmin=box_vmin,
        xmax=box_vmax,
        value=box_vmax,
        c=theme('palette.primary'),
        pos="bottom-right",  # type: ignore
        title="Slab Max Value",
    )

    if renderer == "pyqt":
        plt.show()
        return plt

    l, u = state["slabs"][0].metadata["slab_range"]
    slab_path = os.path.join(experiment.base, f"{volumes_info[0][0]}_slab_{l}_{u}.png")
    show(state["slabs"][0]).screenshot(slab_path).close()


def dynamic_slab(
    experiment: Experiment,
    channel_names: list[str] | str,
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
):
    names = [channel_names] if isinstance(channel_names, str) else list(channel_names)
    by_name = {c.channel_name: c for c in experiment.channels}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise ValueError(f"Channel(s) {missing} not found on this experiment.")
    info = [
        (n, os.path.join(experiment.base, by_name[n].clean_path or by_name[n].path))
        for n in names
    ]
    return _dynamic_slab(experiment, info, renderer, outside_class)