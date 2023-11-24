import os
import json
from vedo import ask, dataurl, printc, settings, show
from vedo import Axes, Mesh, Volume, Box, LinearTransform
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

################################################
refname = dataurl + "270.vtk"
filename = "../data/HCR/HCR12_8a_sox9_594.tif"
iso_value = 145  # isosurface value

################################################
settings.default_font = "Calco"
settings.annotated_cube_texts = [
    "Distal", "Proxim", "Anter", "Poster", "Dorso", "Ventral"]
settings.annotated_cube_text_scale = 0.18

# Read volume
basename = "../data/HCR/" + os.path.basename(filename).replace(".tif", ".vti")
if os.path.exists(basename):  # load existing volume
    vol = Volume(basename)
else:
    printc("Run the first algorithm!")
    exit()

# load transformation matrix and apply it to volume
tname = filename.replace(".tif", ".mat")
T = LinearTransform(tname).print()
vol.apply_transform(T, interpolation='cubic')

iso = vol.isosurface(iso_value).color("blue5", 0.2)

# Compare with reference
reference = Mesh(refname).color("yellow5", 0.2)
vaxes = Axes(vol, xygrid=False, htitle=filename.replace("_", "-"))
slab = vol.slab([350, 355], axis='z', operation='mean')
bbox = slab.metadata["slab_bounding_box"]
slab.z(-bbox[5]+vol.zbounds()[0])  # move slab to the bottom
slab_box = Box(bbox).wireframe().c("black")
slab.cmap('Set1_r', vmin=50, vmax=400).add_scalarbar("slab")

# histogram(slab).show().close()  # quickly inspect it

show(vol, iso, reference, slab, slab_box, vaxes, axes=5, zoom=1.5)