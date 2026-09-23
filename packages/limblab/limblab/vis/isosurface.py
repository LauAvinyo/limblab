from typing import Any, Literal, Optional

import matplotlib.colors as mcolors
import numpy as np
import os
import shutil
from limblab.models import Channel, Experiment
from limblab.vizutils import file2dic, pick_evenly_distributed_values, styles
from vedo import (
    LinearTransform,
    Mesh,
    NonLinearTransform,
    Plotter,
    Text2D,
    Volume,
    printc,
    progressbar
)
from vedo.applications import IsosurfaceBrowser
from limblab.design import theme
from limblab.utils import generate_kwargs

color1 = "#9ce4f3"
color2 = "#128099"
# color1 = "#B9E9EC"
# color2 = "#1C93AE"
primary = "#0d1b2a"
secondary = "#1b263b"
background = "#fb8f00"

CHANNEL_COLORS = ["#B0DB43", "#DB43B0", "#43B0DB", "#F2A93B", "#8E6BF2", "#F25C5C"]


def _two_chanel_isosurface(folder, volume_path_0, volume_path_1, channel_0, channel_1):
    # Get the paths
    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    transformation = pipeline.get("TRANSFORMATION", False)

    # TODO: Take this out of here
    def compute_isosurfaces(volume_path, isosurface_folder):
        # .replace(".vti", "_smooth.vti"))
        volume = Volume(volume_path)
        txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
        plt1 = IsosurfaceBrowser(volume, use_gpu=True, c="gold")
        txt.text("Select the lower isovalue, then press 'q' to confirm")
        plt1.show(txt, axes=7, bg2="lb")
        low_iso_value = int(plt1.sliders[0][0].value)

        # plt2 = IsosurfaceBrowser(volume, use_gpu=True, c='gold')
        txt.text("Select the upper isovalue, then press 'q' to confirm")
        plt1.show(txt, axes=7, bg2="lb")
        high_iso_value = int(plt1.sliders[0][0].value)
        plt1.close()

        v0 = low_iso_value
        v1 = high_iso_value

        # print(
        #     f"""    The lowest isovalue is: {v0}.
        #         The highst isovalue is {v1}.
        #         The resolution is 10% of the values"""
        # )

        arr = np.arange(v0, v1)
        picked_values = pick_evenly_distributed_values(arr)

        if os.path.exists(isosurface_folder):
            shutil.rmtree(isosurface_folder)
        os.makedirs(isosurface_folder)

        printc(
            "Computing isosurfaces and saving files to the isosurface folder...", c="y"
        )
        for iso_val in picked_values:
            surf = volume.isosurface(iso_val)
            surf.write(os.path.join(isosurface_folder, f"{int(iso_val)}.vtk"))

    def interpolate_colors(color1, color2, num_values):
        # Convert input colors to RGB
        rgb1 = np.array(mcolors.to_rgb(color1))
        rgb2 = np.array(mcolors.to_rgb(color2))

        # Generate linearly spaced values between the two colors
        interpolated_colors = [
            rgb1 + (rgb2 - rgb1) * i / (num_values - 1) for i in range(num_values)
        ]

        # Convert RGB values back to hexadecimal format
        interpolated_colors_hex = [
            mcolors.to_hex(color) for color in interpolated_colors
        ]

        return interpolated_colors_hex

    def pick_values(arr, min_val, max_val, num_values):
        # Ensure the array is sorted
        arr = np.sort(arr)

        # Find the closest values to min_val and max_val
        min_idx = (np.abs(arr - min_val)).argmin()
        max_idx = (np.abs(arr - max_val)).argmin()

        # Ensure min_idx is less than max_idx
        if min_idx > max_idx:
            min_idx, max_idx = max_idx, min_idx

        # Generate indices for evenly spaced values
        indices = np.linspace(min_idx, max_idx, num=num_values, dtype=int)

        # Pick the values from the array
        picked_values = arr[indices]

        return picked_values

    def load_isosurfaces(isosurface_folder, transformation, channel):

        # Read array
        all_files = os.listdir(isosurface_folder)
        file_names = [
            f for f in all_files if os.path.isfile(os.path.join(isosurface_folder, f))
        ]
        isovalues = np.sort(np.array([int(os.path.splitext(f)[0]) for f in file_names]))

        # Load isosurfaces
        isosurfaces = {}
        for isovalue in progressbar(isovalues, title="Loading isosurfaces..."):
            surface = Mesh(os.path.join(isosurface_folder, f"{isovalue}.vtk"))
            surface.name = f"{isovalue}_{channel}"
            isosurfaces[f"{isovalue}_{channel}"] = (
                surface.alpha(0.3).lighting("off").frontface_culling()
            )
            if transformation:
                if "morphing" in transformation:
                    T = NonLinearTransform(os.path.join(folder, transformation))
                else:
                    T = LinearTransform(os.path.join(folder, transformation))
                isosurfaces[f"{isovalue}_{channel}"].apply_transform(T)

        return isosurfaces, isovalues

    # Check if the surfaces are computed
    isosurface_folder_0 = os.path.join(folder, f"isosurfaces_{channel_0}")
    isosurface_folder_1 = os.path.join(folder, f"isosurfaces_{channel_1}")

    # Compute them if needed
    if not os.path.exists(isosurface_folder_0):
        compute_isosurfaces(volume_path_0, isosurface_folder_0)
    if not os.path.exists(isosurface_folder_1):
        compute_isosurfaces(volume_path_1, isosurface_folder_1)

    # Load isosurfaces
    isosurfaces_0, isovalues_0 = load_isosurfaces(
        isosurface_folder_0, transformation, "0"
    )
    isosurfaces_1, isovalues_1 = load_isosurfaces(
        isosurface_folder_1, transformation, "1"
    )

    isosurfaces = {0: isosurfaces_0, 1: isosurfaces_1}
    isovalues = {0: isovalues_0, 1: isovalues_1}

    # Load the limb surface
    surface = os.path.join(folder, pipeline.get("BLENDER", pipeline["SURFACE"]))

    limb = Mesh(surface)
    limb.color(styles["limb"]["color"]).alpha(0.1)
    limb.extract_largest_region()
    if transformation:
        if "morphing" in transformation:
            T = NonLinearTransform(os.path.join(folder, transformation))
        else:
            T = LinearTransform(os.path.join(folder, transformation))
        limb.apply_transform(T)

    number_isosurfaces = {0: 3, 1: 3}
    static_limit_values = {
        0: (isovalues_0.min(), isovalues_0.max()),
        1: (isovalues_1.min(), isovalues_1.max()),
    }

    dynamic_limit_values = {
        0: [isovalues_0.min(), isovalues_0.max()],
        1: [isovalues_1.min(), isovalues_1.max()],
    }

    # Create the plotter an add initial isosurfaces
    plt = Plotter(bg="white", shape=(1, 3))
    limb.frontface_culling()
    plt += __doc__
    limb.color(styles["limb"]["alpha"]).alpha(styles["limb"]["alpha"])
    plt.at(0).add(limb)
    plt.at(1).add(limb)
    plt.at(2).add(limb)

    # Toggle the limb funciton
    def limb_toggle_fun(obj, ename):
        if limb.alpha():
            limb.alpha(0)
        else:
            limb.alpha(styles["limb"]["alpha"])
        bu.switch()

    bu = plt.at(2).add_button(
        limb_toggle_fun,
        pos=(0.5, 0.1),  # x,y fraction from bottom left corner
        states=["Hide limb", "Show limb"],  # text for each state
        c=["w", "w"],  # font color for each state
        bc=[
            styles["ui"]["secondary"],
            styles["ui"]["primary"],
        ],  # background color for each state
        font="courier",  # font type
        size=30,  # font size
        bold=True,  # bold font
        italic=False,  # non-italic font style
    )

    # Initial Set of Isovalues
    current_isovalues = {0: [], 1: []}

    def init_isosurfaces(render):
        current_isovalues[render] = pick_values(
            isovalues[render], *dynamic_limit_values[render], number_isosurfaces[render]
        )
        colors = interpolate_colors(*styles[render], number_isosurfaces[render])
        for i, _isovalue in enumerate(current_isovalues[render]):
            plt.at(render).add(
                isosurfaces[render][f"{_isovalue}_{render}"].color(colors[i])
            )
            plt.at(2).add(isosurfaces[render][f"{_isovalue}_{render}"].color(colors[i]))

    init_isosurfaces(0)
    init_isosurfaces(1)

    def clean_plotter(render):
        # global plt, current_isovalues
        for _isovalue in current_isovalues[render]:
            plt.at(render).remove(f"{_isovalue}_{render}")
            plt.at(2).remove(f"{_isovalue}_{render}")

    def add_isosurfaces(render):
        # global plt, number_isosurfaces, current_isovalues
        selected_isovalues = pick_values(
            isovalues[render], *dynamic_limit_values[render], number_isosurfaces[render]
        )
        if number_isosurfaces[render] == 1:
            _isosurface = (
                isosurfaces[render][f"{selected_isovalues[0]}_{render}"]
                .color(styles[render][0])
                .alpha(styles["isosurfaces"]["alpha-unique"])
            )
            plt.at(render).add(_isosurface)
            plt.at(2).add(_isosurface)
        else:
            _colors = interpolate_colors(*styles[render], number_isosurfaces[render])
            for c, _isovalue in enumerate(selected_isovalues):
                _isosurface = (
                    isosurfaces[render][f"{_isovalue}_{render}"]
                    .color(_colors[c])
                    .alpha(styles["isosurfaces"]["alpha"])
                )
                plt.at(render).add(_isosurface)
                plt.at(2).add(_isosurface)
        current_isovalues[render] = selected_isovalues

    def n_surfaces_slider_factory(render):

        def n_surfaces_slider(widget, event):
            number_isosurfaces[render] = np.round(widget.value).astype(int)
            clean_plotter(render)
            add_isosurfaces(render)

        return n_surfaces_slider

    n_surfaces_slider_0 = n_surfaces_slider_factory(0)
    n_surfaces_slider_1 = n_surfaces_slider_factory(1)
    plt.at(0).add_slider(
        n_surfaces_slider_0,
        xmin=1,
        xmax=10,
        value=number_isosurfaces[0],
        c=styles["ui"]["primary"],
        pos=styles["positions"]["number"],
        title="Number of isosurfaces",
        delayed=True,
    )
    plt.at(1).add_slider(
        n_surfaces_slider_1,
        xmin=1,
        xmax=10,
        value=number_isosurfaces[1],
        c=styles["ui"]["primary"],
        pos=styles["positions"]["number"],
        title="Number of isosurfaces",
        delayed=True,
    )

    # Min - max sliders
    def slider_factory(render, limit):
        if not limit in {0, 1}:
            return None
        if limit == 1:

            def slider(widget, event):
                if widget.value > dynamic_limit_values[render][0]:
                    dynamic_limit_values[render][1] = widget.value
                else:
                    dynamic_limit_values[render][1] = (
                        dynamic_limit_values[render][0] + 1
                    )
                    widget.value = dynamic_limit_values[render][1]
                clean_plotter(render)
                add_isosurfaces(render)
        else:

            def slider(widget, event):
                if widget.value < dynamic_limit_values[render][1]:
                    dynamic_limit_values[render][0] = widget.value
                else:
                    dynamic_limit_values[render][0] = (
                        dynamic_limit_values[render][1] - 1
                    )
                    widget.value = dynamic_limit_values[render][0]

                clean_plotter(render)
                add_isosurfaces(render)

        return slider

    min_val_slider_0 = slider_factory(0, 0)
    max_val_slider_0 = slider_factory(0, 1)
    plt.at(0).add_slider(
        min_val_slider_0,
        xmin=static_limit_values[0][0],
        xmax=static_limit_values[0][1],
        value=dynamic_limit_values[1][0],
        c=styles["ui"]["primary"],
        pos=styles["positions"]["values"],
        delayed=True,
        tube_width=0.0015,
        slider_length=0.01,
        slider_width=0.05,
    )
    plt.at(0).add_slider(
        max_val_slider_0,
        xmin=static_limit_values[1][0],
        xmax=static_limit_values[1][1],
        value=dynamic_limit_values[1][1],
        c=styles["ui"]["primary"],
        pos=styles["positions"]["values"],
        title="Min - Max isovalues",
        delayed=True,
        tube_width=0.0015,
        slider_length=0.02,
        slider_width=0.06,
    )

    min_val_slider_1 = slider_factory(1, 0)
    max_val_slider_1 = slider_factory(1, 1)
    plt.at(1).add_slider(
        min_val_slider_1,
        xmin=static_limit_values[1][0],
        xmax=static_limit_values[1][1],
        value=dynamic_limit_values[1][0],
        c=styles["ui"]["primary"],
        pos=styles["positions"]["values"],
        delayed=True,
        tube_width=0.0015,
        slider_length=0.01,
        slider_width=0.05,
    )
    plt.at(1).add_slider(
        max_val_slider_1,
        xmin=static_limit_values[1][0],
        xmax=static_limit_values[1][1],
        value=dynamic_limit_values[1][1],
        c=styles["ui"]["primary"],
        pos=styles["positions"]["values"],
        delayed=True,
        tube_width=0.0015,
        slider_length=0.02,
        slider_width=0.06,
    )

    plt.show().interactive()
    plt.close()


def two_chanel_isosurface(
    experiment: Experiment,
    channel_name_0: str,
    channel_name_1: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> None:

    channels = experiment.channels
    channel_0 = ""
    channel_1 = ""
    for i in channels:
        if i.channel_name == channel_name_0:
            channel_0: Channel = i
        if i.channel_name == channel_name_1:
            channel_1: Channel = i

    volume_path_0 = channel_0.path
    volume_path_1 = channel_1.path
    # pipeline.log (transformation, limb surface) lives next to the volumes
    folder = os.path.dirname(volume_path_0)

    _two_chanel_isosurface(
        folder, volume_path_0, volume_path_1, channel_name_0, channel_name_1
    )



def _pick_values(arr, min_val, max_val, num_values):
    """Pick `num_values` evenly spaced values from `arr` between min_val and max_val."""
    arr = np.sort(arr)
 
    min_idx = int((np.abs(arr - min_val)).argmin())
    max_idx = int((np.abs(arr - max_val)).argmin())
    if min_idx > max_idx:
        min_idx, max_idx = max_idx, min_idx
 
    indices = np.linspace(min_idx, max_idx, num=num_values, dtype=int)
    return arr[indices]
 
 
def _interpolate_colors(color1, color2, num_values):
    if num_values < 2:
        return [mcolors.to_hex(mcolors.to_rgb(color1))] * max(num_values, 0)
    rgb1 = np.array(mcolors.to_rgb(color1))
    rgb2 = np.array(mcolors.to_rgb(color2))
    interpolated = [rgb1 + (rgb2 - rgb1) * i / (num_values - 1) for i in range(num_values)]
    return [mcolors.to_hex(c) for c in interpolated]



####################################################################################################
###############################################UI USED##############################################
####################################################################################################

def _compute_isosurfaces(channel, clean_path, isosurface_folder):
    volume = Volume(clean_path)

    # Prefer isovalue bounds already persisted on the channel row;
    # otherwise pick them interactively.
    need_low = channel.clean_isovalue_min is None
    need_high = channel.clean_isovalue_max is None

    txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
    plt1 = IsosurfaceBrowser(volume, use_gpu=True, c="gold") if (need_low or need_high) else None

    if need_low:
        txt.text(f"[{channel.channel_name}] Select the lower isovalue, then press 'q' to confirm")
        plt1.show(txt, axes=7, bg2="lb")
        low_iso_value = int(plt1.sliders[0][0].value)
    else:
        low_iso_value = channel.clean_isovalue_min

    if need_high:
        txt.text(f"[{channel.channel_name}] Select the upper isovalue, then press 'q' to confirm")
        plt1.show(txt, axes=7, bg2="lb")
        high_iso_value = int(plt1.sliders[0][0].value)
    else:
        high_iso_value = channel.clean_isovalue_max

    if plt1 is not None:
        plt1.close()

    arr = np.arange(int(low_iso_value), int(high_iso_value))
    picked_values = _pick_values(arr, arr.min(), arr.max(), min(len(arr), 20))
    printc(f"Selected isovalues ({channel.channel_name}): {picked_values}", c="cyan")

    if os.path.exists(isosurface_folder):
        shutil.rmtree(isosurface_folder)
    os.makedirs(isosurface_folder)

    printc("Computing isosurfaces and saving files...")
    for iso_val in picked_values:
        surf = volume.isosurface(iso_val)
        surf.write(os.path.join(isosurface_folder, f"{int(iso_val)}.vtk"))


def _load_isosurfaces(isosurface_folder, transformation, channel_name):
    file_names = [
        f for f in os.listdir(isosurface_folder)
        if os.path.isfile(os.path.join(isosurface_folder, f))
    ]
    isovalues = np.sort(np.array([int(os.path.splitext(f)[0]) for f in file_names]))

    T = LinearTransform(transformation) if transformation else None
    isosurfaces = {}
    for isovalue in progressbar(isovalues, title=f"Loading isosurfaces ({channel_name})..."):
        surface = Mesh(os.path.join(isosurface_folder, f"{isovalue}.vtk"))
        surface.name = f"{channel_name}_{isovalue}"      # unique across channels
        isosurfaces[isovalue] = surface.alpha(0.3).lighting("off")
        if T is not None:
            isosurfaces[isovalue].apply_transform(T)
    return isosurfaces, isovalues


class _IsoLayer:
    """Isosurface state of ONE channel (replaces the old module-level globals)."""

    def __init__(self, name, isosurfaces, isovalues, color1, color2, n=8):
        self.name = name
        self.isosurfaces = isosurfaces
        self.isovalues = isovalues
        self.color1, self.color2 = color1, color2
        self.static_min, self.static_max = isovalues.min(), isovalues.max()
        self.vmin, self.vmax = self.static_min, self.static_max
        self.n = n
        self.current = []
        self.plt = None

    def refresh(self):
        for iv in self.current:
            self.plt.remove(self.isosurfaces[iv])
        selected = _pick_values(self.isovalues, self.vmin, self.vmax, self.n)
        if not selected.shape[0]:
            printc(f"No isosurfaces found in the selected range ({self.name}).", c="r")
        colors = _interpolate_colors(self.color1, self.color2, self.n)
        for i, iv in enumerate(selected):
            self.plt.add(self.isosurfaces[iv].color(colors[i]))
        self.current = list(selected)

    def on_min(self, widget, event):
        if widget.value < self.vmax:
            self.vmin = widget.value
        else:
            self.vmin = self.vmax - 1
            widget.value = self.vmin
        self.refresh()

    def on_max(self, widget, event):
        if widget.value > self.vmin:
            self.vmax = widget.value
        else:
            self.vmax = self.vmin + 1
            widget.value = self.vmax
        self.refresh()

    def on_count(self, widget, event):
        self.n = int(np.round(widget.value))
        self.refresh()


def _multi_channel_isosurface(
    experiment: Experiment,
    channels: list[Channel],
    outside_class: Optional[Any] = None,
    renderer: Optional[Literal['pyqt']] = None,
):
    # experiment.linear_transform holds the path to the transform file (if any)
    transformation = experiment.linear_transform
    if transformation:
        transformation = os.path.join(experiment.base, transformation)

    layers = []
    for k, channel in enumerate(channels):
        clean_path = (
            os.path.join(experiment.base, channel.clean_path) if channel.clean_path else None
        )
        if not clean_path or not os.path.exists(clean_path):
            raise FileNotFoundError(
                f"Channel '{channel.channel_name}' has no valid clean_path: {clean_path!r}"
            )

        iso_folder = os.path.join(
            os.path.dirname(clean_path), f"isosurfaces_{channel.channel_name}"
        )
        if not os.path.exists(iso_folder):
            _compute_isosurfaces(channel, clean_path, iso_folder)
        isosurfaces, isovalues = _load_isosurfaces(iso_folder, transformation, channel.channel_name)

        if len(channels) == 1:
            c1, c2 = "#B0DB43", "#DB43B0"          # original single-channel look
        else:
            c1 = CHANNEL_COLORS[k % len(CHANNEL_COLORS)]
            c2 = mcolors.to_hex(np.array(mcolors.to_rgb(c1)) * 0.45)
        layers.append(_IsoLayer(channel.channel_name, isosurfaces, isovalues, c1, c2))

    if not experiment.surface_path:
        raise ValueError(
            f"Experiment '{experiment.experiment_id}' has no surface_path set."
        )
    surface_path = os.path.join(experiment.base, experiment.surface_path)
    if not os.path.exists(surface_path):
        raise FileNotFoundError(
            f"Experiment '{experiment.experiment_id}' surface_path does not exist: "
            f"{surface_path!r}"
        )
    limb = Mesh(surface_path)
    limb.color(styles["limb"]["color"]).alpha(styles["limb"]["alpha"])
    limb.extract_largest_region()
    if transformation:
        limb.apply_transform(LinearTransform(transformation))

    params = generate_kwargs({
        "bg": theme("palette.background"),
        "axes": 14
    })
    kwargs = generate_kwargs(params, renderer, outside_class)

    plt = Plotter(**kwargs)
    plt += limb

    for k, layer in enumerate(layers):
        layer.plt = plt
        layer.refresh()

        y = 0.05 + 0.07 * k          # one row of sliders per channel
        style = dict(delayed=True, tube_width=0.0015, c=layer.color1)
        plt.add_slider(
            layer.on_min,
            xmin=layer.static_min,
            xmax=layer.static_max,
            value=layer.vmin,
            pos=([0.05, y], [0.35, y]),
            slider_length=0.01,
            slider_width=0.05,
            **style,
        )
        plt.add_slider(
            layer.on_max,
            xmin=layer.static_min,
            xmax=layer.static_max,
            value=layer.vmax,
            pos=([0.05, y], [0.35, y]),
            title=f"{layer.name}: min - max isovalues",
            slider_length=0.02,
            slider_width=0.06,
            **style,
        )
        plt.add_slider(
            layer.on_count,
            xmin=2,
            xmax=10,
            value=layer.n,
            pos=([0.45, y], [0.65, y]),
            title=f"{layer.name}: n surfaces",
            delayed=True,
            c=layer.color1,
        )

    def limb_toggle_fun(obj, ename):
        if limb.alpha():
            limb.alpha(0)
        else:
            limb.alpha(styles["limb"]["alpha"])
        bu.switch()

    bu = plt.add_button(
        limb_toggle_fun,
        pos=(0.5, 0.9),
        states=["Hide limb", "Show limb"],
        c=["w", "w"],
        bc=[styles["ui"]["secondary"], styles["ui"]["primary"]],
        font="courier",
        size=30,
        bold=True,
        italic=False,
    )

    plt.show()
    return plt


def one_channel_isosurface(
    experiment: Experiment,
    channel_names: list[str] | str,
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
):
    """Name kept so existing imports keep working; accepts one or many channels."""
    names = [channel_names] if isinstance(channel_names, str) else list(channel_names)
    by_name = {c.channel_name: c for c in experiment.channels}
    missing = [n for n in names if n not in by_name]
    if missing:
        raise ValueError(
            f"Channel(s) {missing} not found on experiment '{experiment.experiment_id}'."
        )
    channels = [by_name[n] for n in names]
    return _multi_channel_isosurface(
        experiment, channels, outside_class=outside_class, renderer=renderer
    )