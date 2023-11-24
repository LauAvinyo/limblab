import os

import json
from vedo import (
    Mesh,
    Volume,
    ask,
    dataurl,
    printc,
    settings,
    show,
    LinearTransform,
)
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

################################################
refname = dataurl + "270.vtk"
filename = "HCR12_8a_sox9_594.tif"
tname = filename.replace(".tif", ".mat")
print(tname)
side = "L"  # Left or Right limb
iso_value = 0  # isosurface value, 0=automatic
spacing = (0.65, 0.65, 2)
# size    = (1024, 1024, 296)  # high res
size = (512, 512, 296)  # low res
clip_range = (60, 600)

################################################
settings.default_font = "Calco"


# Read volume
basename = os.path.basename(filename).replace(".tif", ".vti")
if os.path.exists(basename):  # load existing volume
    vol = Volume(basename)
else:
    printc("Run the first algorithm!")

# plt = IsosurfaceBrowser(vol, use_gpu=True, scalar_range=clip_range)
# plt.show(axes=14).close()

tr = LinearTransform(tname)
vol.apply_transform(tr.T)


# Compare with reference
reference = Mesh(refname)
show(vol, reference, axes=14)
