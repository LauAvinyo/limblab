"""Limb Isolines"""
import os
import sys
from utils import file2dic, pick_evenly_distributed_values
import numpy as np
from vedo import Volume, LinearTransform, Mesh, Plotter, progressbar, Text2D
import matplotlib.colors as mcolors
import numpy as np
import shutil

from vedo.applications import IsosurfaceBrowser

# COLORS #
color1 = "#9ce4f3"
color2 = "#128099"
# color1 = "#B9E9EC"
# color2 = "#1C93AE"
primary = "#0d1b2a"
secondary = "#1b263b"
background = "#fb8f00"

if len(sys.argv) > 3:
    print("Usage: python script_name.py folder_name")
    sys.exit(1)
folder = sys.argv[1]
channel = "SOX9"
if len(sys.argv) == 3:
    channel = sys.argv[2].upper()

# Get the paths
pipeline_file = os.path.join(folder, "pipeline.log")
# pipeline_file = os.path.join(folder, "pipeline.txt")
pipeline = file2dic(pipeline_file)
transformation = pipeline.get("TRANSFORMATION", False)

# Check if the surfaces are computes:

if channel != "SOX9":
    isosurface_folder = os.path.join(folder, f"isosurfaces_{channel}")
else:
    isosurface_folder = os.path.join(folder, f"isosurfaces")


def compute_isosurfaces(logs, channel):
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
    compute_isosurfaces(pipeline, channel)

# Load isosurfaces
# isosurface_folder = os.path.join(folder, "isosurfaces")
isosurfaces, isovalues = load_isosurfaces(isosurface_folder, transformation)

# Load volume

surface = os.path.join(folder, pipeline.get("BLENDER", pipeline["SURFACE"]))

limb = Mesh(surface)
limb.color(background).alpha(0.1)
limb.extract_largest_region()
if transformation:
    T = LinearTransform(os.path.join(folder, transformation))
    limb.apply_transform(T)

# Create plotter and compute the silute
plt = Plotter(bg="white")
limb.frontface_culling()
plt += limb.color("#FF7F11").alpha(0.1)

# silh = limb.silhouette()
# plt += silh

# Ploter
plt += __doc__

number_isosurfaces = 8
vmin = isovalues.min()
vmax = isovalues.max()
max_value = vmax
min_value = vmin


def clean_plotter():
    global plt, current_isovalues
    for isovalue in current_isovalues:
        plt.remove(str(isovalue))


def add_isosurfaces():
    global plt, number_isosurfaces, current_isovalues, min_value, max_value
    selected_isovalues = pick_values(isovalues, min_value, max_value,
                                     number_isosurfaces)
    colors = interpolate_colors(color1, color2, number_isosurfaces)
    if not (selected_isovalues.shape[0]):
        print("Oh no! There is no isosurfaces found!")
    for i, isovalue in enumerate(selected_isovalues):
        plt += isosurfaces[isovalue].color(colors[i])
    current_isovalues = selected_isovalues


def min_val_slider(widget, event):
    global max_value, min_value

    if widget.value < max_value:
        min_value = widget.value
    else:
        min_value = max_value - 1
        widget.value = min_value

    clean_plotter()
    add_isosurfaces()


def max_val_slider(widget, event):
    global max_value, min_value

    if widget.value > min_value:
        max_value = widget.value
    else:
        max_value = min_value + 1
        widget.value = max_value

    clean_plotter()
    add_isosurfaces()


def n_surfaces_slider(widget, event):
    global current_isovalues, number_isosurfaces
    number_isosurfaces = np.round(widget.value).astype(int)

    clean_plotter()
    add_isosurfaces()


# Initial isovalues
current_isovalues = pick_values(isovalues, min_value, max_value,
                                number_isosurfaces)
colors = interpolate_colors(color1, color2, number_isosurfaces)
for i, isovalue in enumerate(current_isovalues):
    plt += isosurfaces[isovalue].color(colors[i])

plt.add_slider(
    min_val_slider,
    xmin=vmin,
    xmax=vmax,
    value=min_value,
    c=primary,
    pos=([0.1, 0.1], [0.4, 0.1]),
    delayed=True,
    tube_width=0.0015,
    slider_length=0.01,
    slider_width=0.05,
)

plt.add_slider(
    max_val_slider,
    xmin=vmin,
    xmax=vmax,
    value=max_value,
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
    value=number_isosurfaces,
    c=secondary,
    pos="bottom-right-vertical",  # type: ignore
    title="Number isolines",
    delayed=True)

plt.show()
plt.close()

# reference_stage = closest_value(reference_stages, int(stage))
# print(
#     f"The stage of the limb is {stage} and we are using as reference {reference_stage}.")
# refence_limb = get_reference_limb(reference_stage)
# print(f"The reference limb is in file {refence_limb}.")

# target = (
#     vedo.Mesh(refence_limb)
#     .cut_with_plane(origin=(1, 0, 0))
#     .color("yellow5")
# )
# plt += target.alpha(0.5).color("green4")
