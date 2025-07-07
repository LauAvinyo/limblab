"""Limb Isolines"""
import json
import os
import shutil
import sys

import matplotlib.colors as mcolors
import numpy as np
from vedo import (Axes, Box, Line, LinearTransform, Mesh, NonLinearTransform,
                  PlaneCutter, Plotter, Text2D, Volume, printc, progressbar,
                  show)
from vedo.applications import (IsosurfaceBrowser, RayCastPlotter,
                               Slicer3DPlotter)
from vedo.pyplot import plot

from limblab.utils import file2dic, pick_evenly_distributed_values  # styles

styles = {
    0: ("#9ce4f3", "#128099"),
    1: ("#ec96f2", "#c90dd6"),
    "postions": {
        "number": ([0.1, 0.25], [0.2, 0.25]),
        "values": ([0.1, 0.1], [0.2, 0.1])
    },
    "channel_0": {
        "color": "#B0DB43"
    },
    "channel_1": {
        "color": "#db43b0"
    },
    "channel_2": {
        "color": "#43b0db"
    },
    "limb": {
        "alpha": 0.1,
        "color": "#FF7F11"
    },
    "reference": {
        "alpha": 1,
        "color": 1
    },
    "isosurfaces": {
        "alpha": 0.3,
        "alpha-unique": 0.8
    },
    "ui": {
        "primary": "#0d1b2a",
        "secondary": "#fb8f00"
    }
}

# from vedo.utils import camera_from_dict


def closest_value(input_list, target):
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest


def get_stage_to_angle_dict(start_x, end_x, start_y, end_y):
    x_values = np.arange(start_x, end_x + 1).astype(int)
    y_values = np.linspace(start_y, end_y, num=len(x_values),
                           dtype=int)  # Ensure integer y-values
    return {int(x): int(y) for x, y in zip(x_values, y_values)}


angle_d = get_stage_to_angle_dict(248, 320, 20, 40)

# top_camera_dict = dict(
#     pos=(727.761, -61.7969, 7909.93),
#     focal_point=(727.761, -61.7969, 33.5966),
#     viewup=(-2.46519e-32, 1.00000, 5.69320e-48),
#     roll=-1.41245e-30,
#     distance=7876.33,
#     clipping_range=(5572.78, 10795.0),
# )
# top_camera_slab = camera_from_dict(top_camera_dict)

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


# import os

# import numpy as np
# from some_module import Volume, file2dic  # Replace with actual module import
# from vedo import Line, plot, show


def probe(folder, channels, points=None):
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
        # TODO: Make the y axis dinamyc
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
                    like=_plot)

        fig = fig.shift(0, 25, 0).clone2d()
        fig.name = "figure"
        plt += fig

    # Add the spline tool using the same points and interact with it
    sptool = plt.add_spline_tool(pts, closed=True)

    # Add a callback to print the center of mass of the spline
    sptool.add_observer(
        "end of interaction",
        lambda o, e: (update_probe(sptool.spline().vertices)),
    )

    # Stay in the loop until the user presses q
    plt.interactive()

    # Switch off the tool
    sptool.off()

    # Extract and visualize the resulting spline
    sp = sptool.spline().lw(4)
    sp.write(os.path.join(folder, "spline.vti"))
    # show(sp, "My spline is ready!", interactive=True, resetcam=False).close()


def _probe(folder, channel, points=None):
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
        print(vertices)
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
        lambda o, e: (update_probe(sptool.spline().vertices)),
    )

    # Stay in the loop until the user presses q
    plt.interactive()

    # Switch off the tool
    sptool.off()

    # Extract and visualize the resulting spline
    sp = sptool.spline().lw(4)
    sp.write(os.path.join(folder, "spline.vti"))
    show(sp, "My spline is ready!", interactive=True, resetcam=False).close()


def one_channel_isosurface(folder, channel):

    # Get the pipeline and the paths
    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    isosurface_folder = os.path.join(folder, f"isosurfaces_{channel}")
    transformation = pipeline.get("ROTATION", False)

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

        arr = np.arange(v0, v1)
        picked_values = pick_evenly_distributed_values(arr)
        print("Picked values:", picked_values)

        if os.path.exists(isosurface_folder):
            shutil.rmtree(isosurface_folder)
        os.makedirs(isosurface_folder)

        printc("Computing and writing the isosurfaces")
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
                "off")  #.frontface_culling()
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
    print("Debug dynamic slab")
    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    surface = pipeline["SURFACE"]
    stage = pipeline["STAGE"]
    volume = os.path.join(folder, pipeline[channel.upper()])

    CMAP = "Greys"
    print(volume)
    vol = Volume(volume)  # .resize([100, 100, 100])
    print("Volume loaded")

    # TODO: Uncomment this
    # # Apply non linear tranformation
    # tname = os.path.join(folder, pipeline["TRANSFORMATION"])
    # if "rotation" in pipeline["TRANSFORMATION"]:
    #     T = LinearTransform(tname)
    # elif "morphing" in pipeline["TRANSFORMATION"]:
    #     T = NonLinearTransform(tname)
    # else:
    #     print("No transformation found... exit")
    #     exit()

    tname = os.path.join(folder, pipeline["ROTATION"])
    T = LinearTransform(tname)
    print("Rotation loaded")

    
    vol.apply_transform(T)
    vol.rotate_y(-angle_d[int(stage)])
    print("Rotation applied!")
    
    
    

    # Load the limb surface
    surface = os.path.join(folder, pipeline.get("BLENDER",
                                                pipeline["SURFACE"]))

    limb = Mesh(surface)
    limb.color(styles["limb"]["color"]).alpha(0.1)
    limb.extract_largest_region()
    limb.apply_transform(T)
    limb.rotate_y(-angle_d[int(stage)])
    vaxes = Axes(
        vol,
        xygrid=False,
    )  # htitle=volume.replace("_", "-")
    print("Surface Loaded")
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
    print("Ready to show!")
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


def multi_channel_isosurface(folder, channels):
    """Compute and visualize isosurfaces for multiple channels."""

    # Get the paths
    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    transformation = pipeline.get("TRANSFORMATION", False)

    def compute_isosurfaces(logs, channel, isosurface_folder):
        volume_file = os.path.join(folder, logs[channel])
        volume = Volume(volume_file)

        txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
        plt1 = IsosurfaceBrowser(volume, use_gpu=True, c='gold')
        txt.text("Pick the lower intensity for the isovalues")
        plt1.show(txt, axes=7, bg2='lb')
        low_iso_value = int(plt1.sliders[0][0].value)

        txt.text("Pick the higher intensity for the isovalues")
        plt1.show(txt, axes=7, bg2='lb')
        high_iso_value = int(plt1.sliders[0][0].value)
        plt1.close()

        v0 = low_iso_value
        v1 = high_iso_value

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
        rgb1 = np.array(mcolors.to_rgb(color1))
        rgb2 = np.array(mcolors.to_rgb(color2))

        interpolated_colors = [
            rgb1 + (rgb2 - rgb1) * i / (num_values - 1)
            for i in range(num_values)
        ]

        interpolated_colors_hex = [
            mcolors.to_hex(color) for color in interpolated_colors
        ]

        return interpolated_colors_hex

    def pick_values(arr, min_val, max_val, num_values):
        arr = np.sort(arr)
        min_idx = (np.abs(arr - min_val)).argmin()
        max_idx = (np.abs(arr - max_val)).argmin()

        if min_idx > max_idx:
            min_idx, max_idx = max_idx, min_idx

        indices = np.linspace(min_idx, max_idx, num=num_values, dtype=int)
        picked_values = arr[indices]

        return picked_values

    def load_isosurfaces(isosurface_folder, transformation, channel):
        all_files = os.listdir(isosurface_folder)
        file_names = [
            f for f in all_files
            if os.path.isfile(os.path.join(isosurface_folder, f))
        ]
        isovalues = np.sort(
            np.array([int(os.path.splitext(f)[0]) for f in file_names]))

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

    # Store isosurface data for each channel
    isosurfaces = {}
    isovalues = {}
    number_isosurfaces = {}
    static_limit_values = {}
    dynamic_limit_values = {}

    # Check if the surfaces are computed and load them
    for i, channel in enumerate(channels):
        isosurface_folder = os.path.join(folder, f"isosurfaces_{channel}")
        if not os.path.exists(isosurface_folder):
            compute_isosurfaces(pipeline, channel, isosurface_folder)

        loaded_isosurfaces, loaded_isovalues = load_isosurfaces(
            isosurface_folder, transformation, i)
        isosurfaces[i] = loaded_isosurfaces
        isovalues[i] = loaded_isovalues

        number_isosurfaces[
            i] = 3  # Initialize with 3 isosurfaces for each channel
        static_limit_values[i] = (loaded_isovalues.min(),
                                  loaded_isovalues.max())
        dynamic_limit_values[i] = [
            loaded_isovalues.min(),
            loaded_isovalues.max()
        ]

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

    # Create the plotter and add initial isosurfaces
    plt = Plotter(bg="white", shape=(1, len(channels) + 1), sharecam=True)
    limb.frontface_culling()
    plt += __doc__
    limb.color(styles["limb"]["alpha"]).alpha(styles["limb"]["alpha"])

    for i in range(len(channels)):
        plt.at(i).add(limb)

    plt.at(len(channels)).add(limb)

    def limb_toggle_fun(obj, ename):
        if limb.alpha():
            limb.alpha(0)
        else:
            limb.alpha(styles["limb"]["alpha"])
        bu.switch()

    bu = plt.at(len(channels)).add_button(
        limb_toggle_fun,
        pos=(0.5, 0.1),
        states=["click to hide limb", "click to show limb"],
        c=["w", "w"],
        bc=[styles["ui"]["secondary"], styles["ui"]["primary"]],
        font="courier",
        size=30,
        bold=True,
        italic=False,
    )

    current_isovalues = {i: [] for i in range(len(channels))}

    def init_isosurfaces(render):
        current_isovalues[render] = pick_values(isovalues[render],
                                                *dynamic_limit_values[render],
                                                number_isosurfaces[render])
        colors = interpolate_colors(*styles[render],
                                    number_isosurfaces[render])
        for i, _isovalue in enumerate(current_isovalues[render]):
            plt.at(render).add(
                isosurfaces[render][f"{_isovalue}_{render}"].color(colors[i]))
            plt.at(len(channels)).add(
                isosurfaces[render][f"{_isovalue}_{render}"].color(colors[i]))

    for i in range(len(channels)):
        init_isosurfaces(i)

    def clean_plotter(render):
        for _isovalue in current_isovalues[render]:
            plt.at(render).remove(f"{_isovalue}_{render}")
            plt.at(len(channels)).remove(f"{_isovalue}_{render}")

    def add_isosurfaces(render):
        selected_isovalues = pick_values(isovalues[render],
                                         *dynamic_limit_values[render],
                                         number_isosurfaces[render])
        if number_isosurfaces[render] == 1:
            _isosurface = isosurfaces[render][
                f"{selected_isovalues[0]}_{render}"].color(
                    styles[render][0]).alpha(
                        styles["isosurfaces"]["alpha-unique"])
            plt.at(render).add(_isosurface)
            plt.at(len(channels)).add(_isosurface)
        else:
            _colors = interpolate_colors(*styles[render],
                                         number_isosurfaces[render])
            for c, _isovalue in enumerate(selected_isovalues):
                _isosurface = isosurfaces[render][
                    f"{_isovalue}_{render}"].color(_colors[c]).alpha(
                        styles["isosurfaces"]["alpha"])
                plt.at(render).add(_isosurface)
                plt.at(len(channels)).add(_isosurface)
        current_isovalues[render] = selected_isovalues

    def n_surfaces_slider_factory(render):

        def n_surfaces_slider(widget, event):
            number_isosurfaces[render] = np.round(widget.value).astype(int)
            clean_plotter(render)
            add_isosurfaces(render)

        return n_surfaces_slider

    for i in range(len(channels)):
        n_surfaces_slider = n_surfaces_slider_factory(i)
        plt.at(i).add_slider(n_surfaces_slider,
                             xmin=1,
                             xmax=10,
                             value=number_isosurfaces[i],
                             pos=styles["postions"]["number"],
                             title="number of isosurfaces")

    def low_threshold_slider_factory(render):

        def low_threshold_slider(widget, event):
            dynamic_limit_values[render][0] = widget.value
            clean_plotter(render)
            add_isosurfaces(render)

        return low_threshold_slider

    for i in range(len(channels)):
        low_threshold_slider = low_threshold_slider_factory(i)
        plt.at(i).add_slider(
            low_threshold_slider,
            xmin=static_limit_values[i][0],
            xmax=static_limit_values[i][1],
            value=dynamic_limit_values[i][0],
            pos=styles["postions"]["values"],
            title="low threshold",
        )

    def high_threshold_slider_factory(render):

        def high_threshold_slider(widget, event):
            dynamic_limit_values[render][1] = widget.value
            clean_plotter(render)
            add_isosurfaces(render)

        return high_threshold_slider

    for i in range(len(channels)):
        high_threshold_slider = high_threshold_slider_factory(i)
        plt.at(i).add_slider(
            high_threshold_slider,
            xmin=static_limit_values[i][0],
            xmax=static_limit_values[i][1],
            value=dynamic_limit_values[i][1],
            pos=styles["postions"]["values"],
            title="high threshold",
        )

    plt.show(interactive=True).close()


# from vedo import *


def arbitary_slice(folder, channel0, channel1):
    normal = [0, 0, 1]

    pipeline_file = os.path.join(folder, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    volume_file0 = os.path.join(folder, pipeline[channel0.upper()])
    volume_file1 = os.path.join(folder, pipeline[channel1.upper()])

    vol0 = Volume(volume_file0)
    vol1 = Volume(volume_file1)

    def func(w, _):
        c, n = pcutter.origin, pcutter.normal
        vslice0 = vol0.slice_plane(c, n,
                                   autocrop=True).cmap("Blues").alpha(0.5)
        vslice0.name = "Slice0"
        vslice1 = vol1.slice_plane(c, n,
                                   autocrop=True).cmap("Oranges").alpha(0.5)
        vslice1.name = "Slice1"
        plt.at(1).remove("Slice0").add(vslice0)
        plt.at(1).remove("Slice1").add(vslice1)

    center = vol0.center()
    vslice0 = vol0.slice_plane(center, normal).cmap("Blues").alpha(0.5)
    vslice0.name = "Slice0"

    vslice1 = vol1.slice_plane(center, normal).cmap("Oranges").alpha(0.5)
    vslice1.name = "Slice1"

    # Create the ploter
    plt = Plotter(axes=0, N=2, bg="k", bg2="bb", interactive=False)
    plt.at(0).show(vol0, vol1, __doc__, zoom=1.5)
    plt.at(1).add(vslice1)

    pcutter = PlaneCutter(
        vslice0,
        normal=normal,
        alpha=0,
        c="white",
        padding=0,
        can_translate=False,
        can_scale=False,
    )
    pcutter.add_observer("interaction", func)
    plt.at(1).add(pcutter)

    plt.interactive()
    plt.close()
