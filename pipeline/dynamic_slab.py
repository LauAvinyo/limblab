import os

from vedo import (
    Axes,
    Box,
    NonLinearTransform,
    Mesh,
    Volume,
    dataurl,
    printc,
    settings,
    grep,
    Plotter,
)


def closest_value(input_list, target):
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest


# TODO: This should be the input
folder = "HCR12_8a_dapi_405"

################################################
pipeline = os.path.join(folder, "pipeline.txt")
# volume = grep(pipeline, "VOLUME")[0][1]
volume = (
    "/Users/lauavino/Documents/PhD/code/sharpe/TOPSECRET/data/HCR/HCR12_8a_sox9_594.vti"
)
surface = grep(pipeline, "SURFACE")[0][1]
stage = int(grep(pipeline, "STAGE")[0][1])

reference_meshes = (250, 260, 270, 290)
reference_stage = closest_value(reference_meshes, int(stage))


################################################
settings.default_font = "Calco"
settings.annotated_cube_texts = [
    "Distal",
    "Proxim",
    "Anter",
    "Poster",
    "Dorso",
    "Ventral",
]
settings.annotated_cube_text_scale = 0.18

# Read volume
if os.path.exists(volume):  # load existing volume
    vol = Volume(volume).resize([100, 100, 100])
else:
    printc("Run the first algorithm!")
    exit()

iso = Mesh(surface).color("blue5", 0.2)
iso_base = iso.clone().color("green3", 0.5)


# Apply non linear tranformation
tname = os.path.join(folder, "nonlinear_transformation.mat")
T = NonLinearTransform(tname)
T.update()
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
slab.cmap("viridis", vmin=50, vmax=400).add_scalarbar("slab")

# histogram(slab).show().close()  # quickly inspect it

# show(vol, iso, reference, slab, slab_box, vaxes, axes=5, zoom=1.5)

plt = Plotter()

plt += vol
plt += iso
plt += reference
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
    slab.cmap("viridis", vmin=50, vmax=400).add_scalarbar("slab")
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
    slab.cmap("viridis", vmin=50, vmax=400).add_scalarbar("slab")
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

# plt.add_slider(
#     slider2,
#     xmin=vmin,
#     xmax=vmax,
#     value=vmax,
#     c=secondary,
#     pos="top-right",  # type: ignore
#     title="Isoline Max value",
# )
