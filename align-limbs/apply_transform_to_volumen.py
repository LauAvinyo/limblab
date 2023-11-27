import os
import json
from vedo import ask, dataurl, printc, settings, show
from vedo import Mesh, Volume, LinearTransform
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

settings.annotated_cube_texts = [
    "Distal",
    "Proxim",
    "Anter",
    "Poster",
    "Dorso",
    "Ventral",
]
settings.annotated_cube_text_scale = 0.18

# NOTE:
# pip install -U git+https://github.com/marcomusy/vedo.git

################################################
refname = dataurl + "270.vtk"
filename = "HCR12_8a_sox9_594.tif"
iso_value = 145  # isosurface value
data_path = "../data/HCR"

################################################
settings.default_font = "Calco"

# Read volume
basename = os.path.join(data_path, os.path.basename(filename).replace(".tif", ".vti"))
print(basename)
if os.path.exists(basename):  # load existing volume
    vol = Volume(basename)
else:
    printc("Run the first algorithm!")
    exit()

# load transformation matrix and apply it to volume
tname = os.path.join(data_path, filename.replace(".tif", ".mat"))
T = LinearTransform(tname).print()
vol.apply_transform(T, interpolation="cubic")

iso = vol.isosurface(iso_value).color("blue5", 0.2)

# Compare with reference
reference = Mesh(refname).color("yellow5", 0.2)
show(vol, iso, reference, axes=5, zoom=1.5)
