import os

from vedo import Volume, dataurl, printc, settings, show, grep
from vedo.pyplot import histogram

# TODO: This should be the input
folder = "HCR12_8a_dapi_405"

################################################
refname = dataurl + "270.vtk"
filename = "HCR12_8a_sox9_594.tif"
side = "L"  # Left or Right limb
iso_value = 0  # isosurface value, 0=automatic
spacing = (0.65, 0.65, 2)
# size    = (1024, 1024, 296)  # high res
size = (512, 512, 296)  # low res
clip_range = (60, 600)
data_path = "../data/HCR"

# Get the the data from the pipeline file
pipeline = os.path.join(folder, "pipeline.txt")
path_volume = grep(pipeline, "VOLUME")[0][1]
iso_value = grep(pipeline, "ISOVAL")[0][1]  # TODO - what if there is no?
iso_value = float(iso_value)

print(path_volume, iso_value)

################################################
settings.default_font = "Calco"

if os.path.exists(path_volume):  # load existing volume
    vol = Volume(path_volume)

else:
    print("You skipt a step!")
    exit()

if not iso_value:
    h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
    iso_value = h.mean

print(vol)

# Computing isosurface
printc(f"-> Computing isosurface... iso_value = {iso_value}", c="pink")
surface = vol.isosurface(iso_value).extract_largest_region()

# Decimating isosurface
print(f"-> Decimating isosurface... from n = {surface.npoints} please wait...")
surface.decimate(0.1)


path_surface = path_volume.replace(".vti", "_surface.vtk")

printc("-> Writing", path_surface)
surface.write(path_surface)
show(surface, axes=14).close()

with open(pipeline, "a") as f:
    print("SURFACE", path_surface, file=f)
