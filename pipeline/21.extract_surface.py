import os
import sys

from utils import dic2file, file2dic
from vedo import Volume, printc, settings
from vedo.pyplot import histogram

settings.default_font = "Calco"


if len(sys.argv) != 2:
    print("Usage: python script_name.py folder_name")
    sys.exit(1)
folder = sys.argv[1]

# Get the paths
pipeline_file = os.path.join(folder, "pipeline.txt")
pipeline = file2dic(pipeline_file)
volume = pipeline["DAPI"]
iso_value = pipeline.get("ISOVAL", 0)


side = "R"  # Should be in the volume Name TODO!


if os.path.exists(volume):
    vol = Volume(volume)
else:
    print("Make sure you clean up DAPI volume!")
    exit()

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
printc(f"-> Decimating isosurface... from n = {surface.npoints} please wait...")
surface.decimate(0.1)


path_surface = volume.replace(".vti", "_surface.vtk")

printc("-> Writing", path_surface)
surface.write(path_surface)
# show(surface, axes=14).close()

# Store the path
pipeline["SURFACE"] = path_surface
dic2file(pipeline, pipeline_file)

# TODO:
# Close the surface
