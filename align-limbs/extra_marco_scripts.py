import os
import json
from vedo import ask, dataurl, printc, settings, show
from vedo import Mesh, Volume, LinearTransform
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

# NOTE:
# pip install -U git+https://github.com/marcomusy/vedo.git

################################################
refname = dataurl + "270.vtk"
filename = "HCR12_8a_sox9_594.tif"
iso_value = 145  # isosurface value

################################################
settings.default_font = "Calco"

# Read volume
basename = os.path.basename(filename).replace(".tif", ".vti")
if os.path.exists(basename):  # load existing volume
    vol = Volume(basename)
else:
    printc("Run the first algorithm!")
    exit()

# load transformation matrix and apply it to volume
tname = filename.replace(".tif", ".mat")
T = LinearTransform(tname).print()
vol.apply_transform(T, interpolation="cubic")

iso = vol.isosurface(iso_value).color("blue5", 0.2)

# Compare with reference
reference = Mesh(refname).color("yellow5", 0.2)
show(vol, iso, reference, axes=14)
