import json
import os
import sys

from utils import file2dic
from vedo import (Axes, Box, Mesh, NonLinearTransform, Plotter, Volume,
                  dataurl, np, show)


def closest_value(input_list, target):
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest


if len(sys.argv) != 3:
    print("Usage: python script_name.py folder_name channel")
    sys.exit(1)

folder = sys.argv[1]
channel = sys.argv[2]

pipeline_file = os.path.join(folder, "pipeline.log")
pipeline = file2dic(pipeline_file)
surface = pipeline["SURFACE"]
stage = pipeline["STAGE"]
volume = pipeline[channel.upper()]

CMAP = "Greys"

reference_meshes = (250, 260, 270, 290)
reference_stage = closest_value(reference_meshes, int(stage))

vol = Volume(volume).resize([100, 100, 100])

iso = Mesh(surface).color("blue5", 0.2)

# Apply non linear tranformation
# tname = os.path.join(folder, "nonlinear_transformation.mat")
T = NonLinearTransform(pipeline["TRANSFORMATION"])
vol.apply_transform(T).rotate_y(-30)
iso.apply_transform(T).rotate_y(-30)

# Compare with reference
reference = Mesh(dataurl + f"{reference_stage}.vtk").color("yellow5", 0.2)
reference.rotate_y(-30)
vaxes = Axes(
    vol,
    xygrid=False,
)  # htitle=volume.replace("_", "-")

# Box
vmin = 0
vmax = 500
box_min = vmin
box_max = vmax
box_limits = [box_min, box_max]
slab = vol.slab(box_limits, axis="z", operation="mean")
bbox = slab.metadata["slab_bounding_box"]
zslab = slab.zbounds()[0] + 1000
slab.z(-zslab)  # move slab to the bottom  # move slab to the bottom
slab_box = Box(bbox).wireframe().c("black")
slab.cmap(CMAP, vmin=50, vmax=400).add_scalarbar("slab")

plt = Plotter()

plt += vol
plt += iso
# plt += reference
plt += slab
plt += slab_box
plt += vaxes


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


plt.add_slider(
    slider1,
    xmin=vmin,
    xmax=vmax,
    value=vmin,
    c="r1",
    pos="bottom-left",  # type: ignore
    title="Isoline Min Value",
)

plt.add_slider(
    slider2,
    xmin=vmin,
    xmax=vmax,
    value=vmax,
    c="r1",
    pos="bottom-right",  # type: ignore
    title="Isoline Max Value",
)

plt.show(axes=14, zoom=1.5).close()

print(slab)


def load_mesh(file):
    with open(file, "r") as f:
        meshes_raw = json.load(f)["morphomovie"]

    mesh = {}
    for m in meshes_raw:
        mesh[round(m["t"])] = {
            "nodes":
            np.array(tuple((x, y) for _, x, y in m["nodes"])),
            "elements":
            np.array(
                tuple((a - 1, b - 1, c - 1) for _, a, b, c in m["elements"])),
        }
    return mesh


l, u = slab.metadata["slab_range"]

slab_path = os.path.join(folder, f"{channel}_slab_{l}_{u}.py")

# One option is to get the screenshot of the slab.
# show(slab).screenshot(slab_path).close()

# Another option is to map it onto the morphomovie and send the mesh to LimbNET
mesh_2d = load_mesh("../data/fineFgfsNorm8.mm.mesh.ol.json")[int(stage) * 60]
msh = Mesh([mesh_2d["nodes"], mesh_2d["elements"]])
msh.z(-zslab)

msh.interpolate_data_from(slab, n=3).cmap("viridis")

show(msh).close()
