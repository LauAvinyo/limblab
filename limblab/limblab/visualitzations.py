"""Limb Isolines"""
import json
import os
import shutil
import sys

import matplotlib.colors as mcolors
import numpy as np
from vedo import (Axes, Box, Line, LinearTransform, Mesh, NonLinearTransform,
                  Plotter, Text2D, Volume, dataurl, np, progressbar, show)
from vedo.applications import (IsosurfaceBrowser, RayCastPlotter,
                               Slicer3DPlotter)
from vedo.pyplot import plot

from limblab.utils import file2dic, pick_evenly_distributed_values, styles


def closest_value(input_list, target):
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest


# def load_mesh(file):
#     with open(file, "r") as f:
#         meshes_raw = json.load(f)["morphomovie"]

#     mesh = {}
#     for m in meshes_raw:
#         mesh[round(m["t"])] = {
#             "nodes":
#             np.array(tuple((x, y) for _, x, y in m["nodes"])),
#             "elements":
#             np.array(
#                 tuple((a - 1, b - 1, c - 1) for _, a, b, c in m["elements"])),
#         }
#     return mesh

# TODO:
# This can be clean up. There are some functions no needed here.
# We can add more funtionality.
# Make a list of the functionlaity we should have.
color1 = "#9ce4f3"
color2 = "#128099"
# color1 = "#B9E9EC"
# color2 = "#1C93AE"
primary = "#0d1b2a"
secondary = "#1b263b"
background = "#fb8f00"


def two_chanel_isosurface(folder, channel_0, channel_1):
    #
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
            rgb1 + (rgb2 - rgb1) * i / (num_values - 1)
            for i in range(num_values)
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
                if "morphing" in transformation:
                    T = NonLinearTransform(os.path.join(
                        folder, transformation))
                else:
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
    surface = os.path.join(folder, pipeline.get("BLENDER",
                                                pipeline["SURFACE"]))

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
        states=["click to hide limb",
                "click to show limb"],  # text for each state
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
        colors = interpolate_colors(*styles[render],
                                    number_isosurfaces[render])
        for i, _isovalue in enumerate(current_isovalues[render]):
            plt.at(render).add(
                isosurfaces[render][f"{_isovalue}_{render}"].color(colors[i]))
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
                    styles[render][0]).alpha(
                        styles["isosurfaces"]["alpha-unique"])
            plt.at(render).add(_isosurface)
            plt.at(2).add(_isosurface)
        else:
            _colors = interpolate_colors(*styles[render],
                                         number_isosurfaces[render])
            for c, _isovalue in enumerate(selected_isovalues):
                _isosurface = isosurfaces[render][
                    f"{_isovalue}_{render}"].color(_colors[c]).alpha(
                        styles["isosurfaces"]["alpha"])
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
        xmin=static_limit_values[0][0],
        xmax=static_limit_values[0][1],
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


def raycast(folder, channel):
    # Load Volume data
    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)

    volume_file = os.path.join(folder, pipeline[channel.upper()])
    volume = Volume(volume_file)
    # TODO: apply transform if so.
    # transformation = pipeline.get("TRANSFORMATION", False)

    volume.mode(1).cmap("jet")  # change visual properties

    # Create a Plotter instance and show
    plt = RayCastPlotter(volume, bg='white', axes=7)
    plt.show(viewup="z")
    plt.close()


def slices(folder, channel):
    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    volume_file = os.path.join(folder, pipeline[channel.upper()])
    volume = Volume(volume_file)

    plt = Slicer3DPlotter(volume,
                          cmaps=("gist_ncar_r", "jet", "Spectral_r", "hot_r",
                                 "bone_r"),
                          use_slider3d=False,
                          bg="white")

    # Can now add any other vedo object to the Plotter scene:
    plt += Text2D(__doc__)

    plt.show(viewup='z')
    plt.close()


def probe(folder, channel, p1=None, p2=None):
    """Probe a Volume with a line and plot the intensity values"""

    # TODO - Make this dynamic
    p1, p2 = (50, 300, 400), (1000, 300, 400)

    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    volume_file = os.path.join(folder, pipeline[channel.upper()])
    volume = Volume(volume_file)
    volume.add_scalarbar3d(channel, c="k")
    volume.scalarbar = volume.scalarbar.clone2d("bottom-right", 0.2)

    pl = Line(p1, p2, res=100).lw(4)

    # Probe the Volume with the line
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

    show(volume, pl, fig, __doc__, axes=14).close()


def one_channel_isosurface(folder, channel):

    # Get the pipeline and the paths
    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    isosurface_folder = os.path.join(folder, f"isosurfaces_{channel}")
    transformation = pipeline.get("TRANSFORMATION", False)

    def compute_isosurfaces(logs, channel, folder, isosurface_folder):
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
        print("Picked values:", picked_values)

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
            rgb1 + (rgb2 - rgb1) * i / (num_values - 1)
            for i in range(num_values)
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

    def load_isosurfaces(isosurface_folder, transformation):

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
            surface.name = str(isovalue)
            isosurfaces[isovalue] = surface.alpha(0.3).lighting(
                "off").frontface_culling()
            if transformation:
                T = LinearTransform(os.path.join(folder, transformation))
                isosurfaces[isovalue].apply_transform(T)

        return isosurfaces, isovalues

    if not os.path.exists(isosurface_folder):
        compute_isosurfaces(pipeline, channel, folder, isosurface_folder)

    # Load the channel isosurfaces
    isosurfaces, isovalues = load_isosurfaces(isosurface_folder,
                                              transformation)

    # Load the limb surface
    surface = os.path.join(folder, pipeline.get("BLENDER",
                                                pipeline["SURFACE"]))
    limb = Mesh(surface)
    limb.color(styles["limb"]["color"]).alpha(0.1)
    limb.extract_largest_region()
    if transformation:
        T = LinearTransform(os.path.join(folder, transformation))
        limb.apply_transform(T)

    plt = Plotter(bg="white")
    limb.frontface_culling()
    plt += limb.color("#FF7F11").alpha(0.1)

    #
    static_min_value = isovalues.min()
    static_max_value = isovalues.max()

    global _dynamic_min_value, _number_isosurfaces, _dynamic_max_value, _current_isovalues
    _number_isosurfaces = 8
    _dynamic_min_value = static_min_value
    _dynamic_max_value = static_max_value

    # Initial isovalues
    _current_isovalues = pick_values(isovalues, _dynamic_min_value,
                                     _dynamic_max_value, _number_isosurfaces)
    colors = interpolate_colors(color1, color2, _number_isosurfaces)
    for i, isovalue in enumerate(_current_isovalues):
        plt += isosurfaces[isovalue].color(colors[i])

    def clean_plotter():
        global _current_isovalues
        for isovalue in _current_isovalues:
            plt.remove(str(isovalue))

    def add_isosurfaces():
        global _number_isosurfaces, _current_isovalues, _dynamic_min_value, _dynamic_max_value
        selected_isovalues = pick_values(isovalues, _dynamic_min_value,
                                         _dynamic_max_value,
                                         _number_isosurfaces)
        colors = interpolate_colors(color1, color2, _number_isosurfaces)
        if not (selected_isovalues.shape[0]):
            print("Oh no! There is no isosurfaces found!")
        for i, isovalue in enumerate(selected_isovalues):
            plt.add(isosurfaces[isovalue].color(colors[i]))
        _current_isovalues = selected_isovalues

    def min_val_slider(widget, event):
        global _dynamic_min_value, _dynamic_max_value
        print(_dynamic_min_value)
        if widget.value < _dynamic_max_value:
            _dynamic_min_value = widget.value
        else:
            _dynamic_min_value = _dynamic_max_value - 1
            widget.value = _dynamic_min_value

        clean_plotter()
        add_isosurfaces()

    def max_val_slider(widget, event):
        global _dynamic_max_value, _dynamic_min_value

        if widget.value > _dynamic_min_value:
            _dynamic_max_value = widget.value
        else:
            _dynamic_max_value = _dynamic_min_value + 1
            widget.value = _dynamic_max_value

        clean_plotter()
        add_isosurfaces()

    def n_surfaces_slider(widget, event):
        global _number_isosurfaces
        _number_isosurfaces = np.round(widget.value).astype(int)

        clean_plotter()
        add_isosurfaces()

    plt.add_slider(
        min_val_slider,
        xmin=static_min_value,
        xmax=static_max_value,
        value=_dynamic_min_value,
        c=styles["ui"]["primary"],
        pos=([0.1, 0.1], [0.4, 0.1]),
        delayed=True,
        tube_width=0.0015,
        slider_length=0.01,
        slider_width=0.05,
    )

    plt.add_slider(
        max_val_slider,
        xmin=static_min_value,
        xmax=static_max_value,
        value=_dynamic_max_value,
        c=secondary,
        pos=([0.1, 0.1], [0.4, 0.1]),
        title="Min - Max isovalues (resolution dependen!)",
        delayed=True,
        tube_width=0.0015,
        slider_length=0.02,
        slider_width=0.06,
    )

    plt.add_slider(
        n_surfaces_slider,
        xmin=2,
        xmax=10,
        value=_number_isosurfaces,
        c=secondary,
        pos="bottom-right-vertical",  # type: ignore
        title="Number isolines",
        delayed=True)

    # Toggle the limb funciton
    def limb_toggle_fun(obj, ename):
        if limb.alpha():
            limb.alpha(0)
        else:
            limb.alpha(styles["limb"]["alpha"])
        bu.switch()

    bu = plt.add_button(
        limb_toggle_fun,
        pos=(0.5, 0.9),  # x,y fraction from bottom left corner
        states=["click to hide limb",
                "click to show limb"],  # text for each state
        c=["w", "w"],  # font color for each state
        bc=[styles["ui"]["secondary"],
            styles["ui"]["primary"]],  # background color for each state
        font="courier",  # font type
        size=30,  # font size
        bold=True,  # bold font
        italic=False,  # non-italic font style
    )

    plt.show().interactive()
    plt.close()


def dynamic_slab(folder, channel):
    print(folder, channel)

    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    surface = pipeline["SURFACE"]
    stage = pipeline["STAGE"]
    volume = os.path.join(folder, pipeline[channel.upper()])

    CMAP = "Greys"

    vol = Volume(volume)  # .resize([100, 100, 100])

    # Apply non linear tranformation
    tname = os.path.join(folder, pipeline["TRANSFORMATION"])
    if "rotation" in pipeline["TRANSFORMATION"]:
        T = LinearTransform(tname)
    elif "morphing" in pipeline["TRANSFORMATION"]:
        T = NonLinearTransform(tname)
    else:
        print("No transformation found... exit")
        exit()

    vol.apply_transform(T).rotate_y(-30)

    # Load the limb surface
    surface = os.path.join(folder, pipeline.get("BLENDER",
                                                pipeline["SURFACE"]))

    limb = Mesh(surface)
    limb.color(styles["limb"]["color"]).alpha(0.1)
    limb.extract_largest_region()
    limb.apply_transform(T)
    limb.rotate_y(-30)
    vaxes = Axes(
        vol,
        xygrid=False,
    )  # htitle=volume.replace("_", "-")

    # Box
    global slab, slab_box, box_limits

    # TODO: Get a bettern min max
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
    slab.cmap(CMAP, vmin=50, vmax=400).add_scalarbar("slab")

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
        slab.cmap(CMAP, vmin=50, vmax=400).add_scalarbar("slab")
        plt.add(slab)
        plt.add(slab_box)

    def slider2(widget, event):
        global slab, slab_box, box_limits

        print(slab, box_limits)
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
        slab.cmap(CMAP, vmin=50, vmax=400).add_scalarbar("slab")
        plt.add(slab)
        plt.add(slab_box)

    plt = Plotter()

    plt += vol
    plt += limb
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

    print(slab)

    # l, u = slab.metadata["slab_range"]

    # slab_path = os.path.join(folder, f"{channel}_slab_{l}_{u}.py")

    # # One option is to get the screenshot of the slab.
    # show(slab).screenshot(slab_path).close()

    # # Another option is to map it onto the morphomovie and send the mesh to LimbNET
    # mesh_2d = load_mesh("../data/fineFgfsNorm8.mm.mesh.ol.json")[int(stage) *
    #                                                              60]
    # msh = Mesh([mesh_2d["nodes"], mesh_2d["elements"]])
    # msh.z(-zslab)

    # msh.interpolate_data_from(slab, n=3).cmap("viridis")

    # show(msh).close()


# if __name__ == "__main__":
#     folder = "/Users/lauavino/Documents/Code/limblab/data/HCR20_BMP2_l1"
#     channel_0 = "SOX9"
#     channel_1 = "BMP2"
#     # two_chanel_isosurface(folder, channel_0, channel_1)
#     # raycast(folder, channel_1)
#     # slices(folder, channel_0)
#     # p1, p2 = (50, 300, 400), (1000, 300, 400)
#     # probe(folder, channel_0, p1, p2)
#     one_channel_isosurface(folder, channel_0)
