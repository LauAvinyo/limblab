import os

from vedo import (
    Axes,
    Box,
    LinearTransform,
    NonLinearTransform,
    Mesh,
    Volume,
    dataurl,
    printc,
    settings,
    show,
    Plotter,
)

################################################
refname = dataurl + "270.vtk"
filename = "../data/HCR/HCR12_8a_sox9_594.tif"
iso_value = 145  # isosurface value

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
basename = "../data/HCR/" + os.path.basename(filename).replace(".tif", ".vti")
if os.path.exists(basename):  # load existing volume
    vol = Volume(basename)
else:
    printc("Run the first algorithm!")
    exit()

# load transformation matrix and apply it to volume
# tname = filename.replace(".tif", ".mat")
tname = "transformation.mat"
T = NonLinearTransform(tname)
T.update()
# print(T)
# exit()
vol.apply_transform(T)

iso = vol.isosurface(iso_value).color("blue5", 0.2)
# iso.apply_transform(T)

# Compare with reference
reference = Mesh(refname).color("yellow5", 0.2)
vaxes = Axes(vol, xygrid=False, htitle=filename.replace("_", "-"))

# Box
vmin = 340
vmax = 400
box_min = vmin
box_max = vmax
box_limits = [box_min, box_max]
slab = vol.slab(box_limits, axis="z", operation="mean")
bbox = slab.metadata["slab_bounding_box"]
slab.z(-bbox[5] + vol.zbounds()[0])  # move slab to the bottom
slab_box = Box(bbox).wireframe().c("black")
slab.cmap("Set1_r", vmin=50, vmax=400).add_scalarbar("slab")

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
    slab.z(-bbox[5] + vol.zbounds()[0])  # move slab to the bottom
    slab_box = Box(bbox).wireframe().c("black")
    slab.cmap("Set1_r", vmin=50, vmax=400).add_scalarbar("slab")
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
    slab.z(-bbox[5] + vol.zbounds()[0])  # move slab to the bottom
    slab_box = Box(bbox).wireframe().c("black")
    slab.cmap("Set1_r", vmin=50, vmax=400).add_scalarbar("slab")
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
