"""Limb Isolines"""
import json
import os
import shutil
import sys

import matplotlib.colors as mcolors
import numpy as np
from utils import file2dic, pick_evenly_distributed_values, styles
from vedo import LinearTransform, Mesh, Plotter, Text2D, Volume, progressbar
from vedo.applications import IsosurfaceBrowser

if len(sys.argv) != 4:
    print("Usage: python script_name.py folder_name CHANNEL_0 CHANNEL_1")
    sys.exit(1)
folder = sys.argv[1]

# Channels
channel_0 = sys.argv[2]
channel_1 = sys.argv[3]

# Get the paths
pipeline_file = os.path.join(folder, "pipeline.log")
pipeline = file2dic(pipeline_file)
transformation = pipeline.get("TRANSFORMATION", False)


# TODO: Take this out of here
def compute_isosurfaces(logs, channel, isosurface_folder):
    # .replace(".vti", "_smooth.vti"))
    volume_file = os.path.join(folder, logs[channel])
    volume = Volume(volume_file)

    txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
    plt1 = IsosurfaceBrowser(volume, use_gpu=True, c='gold')
    txt.text("Pick the lower intensity for the isovalues")
    plt1.show(txt, axes=7, bg2='lb')
    low_iso_value = int(plt1.sliders[0][0].value)

    # plt2 = IsosurfaceBrowser(volume, use_gpu=True, c='gold')
    txt.text("Pick the higher intensity for the isovalues")
    plt1.show(txt, axes=7, bg2='lb')
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

    print("Computing and writing the isosurfaces")
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
        f for f in all_files
        if os.path.isfile(os.path.join(isosurface_folder, f))
    ]
    isovalues = np.sort(
        np.array([int(os.path.splitext(f)[0]) for f in file_names]))

    # Load isosurfaces
    isosurfaces = {}
    for isovalue in progressbar(isovalues, title="Loading surfaces..."):
        surface = Mesh(os.path.join(isosurface_folder, f"{isovalue}.vtk"))
        surface.name = f"{isovalue}_{channel}"
        isosurfaces[f"{isovalue}_{channel}"] = surface.alpha(0.3).lighting(
            "off").frontface_culling()
        if transformation:
            T = LinearTransform(os.path.join(folder, transformation))
            isosurfaces[f"{isovalue}_{channel}"].apply_transform(T)

    return isosurfaces, isovalues


# Check if the surfaces are computed
isosurface_folder_0 = os.path.join(folder, f"isosurfaces_{channel_0}")
isosurface_folder_1 = os.path.join(folder, f"isosurfaces_{channel_1}")

# Compute them if needed
if not os.path.exists(isosurface_folder_0):
    compute_isosurfaces(pipeline, channel_0, isosurface_folder_0)
if not os.path.exists(isosurface_folder_1):
    compute_isosurfaces(pipeline, channel_1, isosurface_folder_1)

# Load isosurfaces
isosurfaces_0, isovalues_0 = load_isosurfaces(isosurface_folder_0,
                                              transformation, "0")
isosurfaces_1, isovalues_1 = load_isosurfaces(isosurface_folder_1,
                                              transformation, "1")

isosurfaces = {0: isosurfaces_0, 1: isosurfaces_1}
isovalues = {0: isovalues_0, 1: isovalues_1}

# Load the limb surface
surface = os.path.join(folder, pipeline.get("BLENDER", pipeline["SURFACE"]))

limb = Mesh(surface)
limb.color(styles["limb"]["color"]).alpha(0.1)
limb.extract_largest_region()
if transformation:
    T = LinearTransform(os.path.join(folder, transformation))
    limb.apply_transform(T)

number_isosurfaces = {0: 3, 1: 3}
static_limit_values = {
    0: (isovalues_0.min(), isovalues_0.max()),
    1: (isovalues_1.min(), isovalues_1.max())
}

dynamic_limit_values = {
    0: [isovalues_0.min(), isovalues_0.max()],
    1: [isovalues_1.min(), isovalues_1.max()]
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
    states=["click to hide limb", "click to show limb"],  # text for each state
    c=["w", "w"],  # font color for each state
    bc=[styles["ui"]["secondary"],
        styles["ui"]["primary"]],  # background color for each state
    font="courier",  # font type
    size=30,  # font size
    bold=True,  # bold font
    italic=False,  # non-italic font style
)

# Initial Set of Isovalues
current_isovalues = {0: [], 1: []}


def init_isosurfaces(render):
    current_isovalues[render] = pick_values(isovalues[render],
                                            *dynamic_limit_values[render],
                                            number_isosurfaces[render])
    colors = interpolate_colors(*styles[render], number_isosurfaces[render])
    for i, _isovalue in enumerate(current_isovalues[render]):
        plt.at(render).add(isosurfaces[render][f"{_isovalue}_{render}"].color(
            colors[i]))
        plt.at(2).add(isosurfaces[render][f"{_isovalue}_{render}"].color(
            colors[i]))


init_isosurfaces(0)
init_isosurfaces(1)


def clean_plotter(render):
    # global plt, current_isovalues
    for _isovalue in current_isovalues[render]:
        plt.at(render).remove(f"{_isovalue}_{render}")
        plt.at(2).remove(f"{_isovalue}_{render}")


def add_isosurfaces(render):
    # global plt, number_isosurfaces, current_isovalues
    selected_isovalues = pick_values(isovalues[render],
                                     *dynamic_limit_values[render],
                                     number_isosurfaces[render])
    if number_isosurfaces[render] == 1:
        _isosurface = isosurfaces[render][
            f"{selected_isovalues[0]}_{render}"].color(
                styles[render][0]).alpha(styles["isosurfaces"]["alpha-unique"])
        plt.at(render).add(_isosurface)
        plt.at(2).add(_isosurface)
    else:
        _colors = interpolate_colors(*styles[render],
                                     number_isosurfaces[render])
        for c, _isovalue in enumerate(selected_isovalues):
            _isosurface = isosurfaces[render][f"{_isovalue}_{render}"].color(
                _colors[c]).alpha(styles["isosurfaces"]["alpha"])
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
plt.at(0).add_slider(n_surfaces_slider_0,
                     xmin=1,
                     xmax=10,
                     value=number_isosurfaces[0],
                     c=styles["ui"]["primary"],
                     pos=styles["postions"]["number"],
                     title="Number isolines",
                     delayed=True)
plt.at(1).add_slider(n_surfaces_slider_1,
                     xmin=1,
                     xmax=10,
                     value=number_isosurfaces[1],
                     c=styles["ui"]["primary"],
                     pos=styles["postions"]["number"],
                     title="Number isolines",
                     delayed=True)


# Min - max sliders
def slider_factory(render, limit):
    if not limit in {0, 1}:
        return None
    if limit == 1:

        def slider(widget, event):
            if widget.value > dynamic_limit_values[render][0]:
                dynamic_limit_values[render][1] = widget.value
            else:
                dynamic_limit_values[render][
                    1] = dynamic_limit_values[render][0] + 1
                widget.value = dynamic_limit_values[render][1]
            clean_plotter(render)
            add_isosurfaces(render)
    else:

        def slider(widget, event):
            if widget.value < dynamic_limit_values[render][1]:
                dynamic_limit_values[render][0] = widget.value
            else:
                dynamic_limit_values[render][
                    0] = dynamic_limit_values[render][1] - 1
                widget.value = dynamic_limit_values[render][0]

            clean_plotter(render)
            add_isosurfaces(render)

    return slider


min_val_slider_0 = slider_factory(0, 0)
max_val_slider_0 = slider_factory(0, 1)
plt.at(0).add_slider(
    min_val_slider_0,
    xmin=static_limit_values[1][0],
    xmax=static_limit_values[1][1],
    value=dynamic_limit_values[1][0],
    c=styles["ui"]["primary"],
    pos=styles["postions"]["values"],
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
    pos=styles["postions"]["values"],
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
    pos=styles["postions"]["values"],
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
    pos=styles["postions"]["values"],
    delayed=True,
    tube_width=0.0015,
    slider_length=0.02,
    slider_width=0.06,
)

plt.show().interactive()
plt.close()
