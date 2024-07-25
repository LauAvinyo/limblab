import os
import sys

from utils import dic2file, file2dic
from vedo import Volume, printc, settings
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

# settings.default_font = "Calco"

if len(sys.argv) != 2:
    print("Usage: python script_name.py folder_name")
    sys.exit(1)
folder = sys.argv[1]

# Get the paths
pipeline_file = os.path.join(folder, "pipeline.log")
pipeline = file2dic(pipeline_file)
volume = pipeline.get("DAPI", False)
path_surface = volume.replace(".vti", "_surface.vtk")

if not Volume:
    print("Make sure you have clean the DAPI channel volume!")
    exit()

volume = os.path.join(folder, volume)

# Read the volume
vol = Volume(volume)

# IsosurfaceBrowser(Plotter) instance:
plt = IsosurfaceBrowser(vol.color("green"), use_gpu=True, c="green", alpha=0.6)
plt.show(axes=7, bg2="lb")

# Get the isosurface value
iso_value = plt.sliders[0][0].value
plt.close()
printc(f"The selected iso value is {iso_value:2f}.", c="orange")

if not iso_value:
    printc(
        "We are using automatic isovalue! You can manually pic one by using 20.get_isovalue.py script!"
    )
    h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
    iso_value = h.mean
iso_value = float(iso_value)

print(vol)

# Computing isosurface
printc(f"-> Computing isosurface... iso_value = {iso_value}", c="orange")
surface = vol.isosurface(iso_value).extract_largest_region()

# Decimating isosurface
printc(
    f"-> Decimating isosurface... from n = {surface.npoints} please wait...")
surface.decimate(0.005)

printc("-> Writing", path_surface)
# surface.write(os.path.join(folder, path_surface))

# TODO:
# Close the surface
