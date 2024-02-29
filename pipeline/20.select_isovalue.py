import os
import sys

from utils import dic2file, file2dic
from vedo import Volume, printc
from vedo.applications import IsosurfaceBrowser

if len(sys.argv) != 2:
    print("Usage: python script_name.py folder_name")
    sys.exit(1)
folder = sys.argv[1]

# Get the paths
pipeline_file = os.path.join(folder, "pipeline.txt")
pipeline = file2dic(pipeline_file)
volume = pipeline.get("DAPI", False)

if not Volume:
    print("Make sure you have clean the DAPI channel volume!")
    exit()


# Read the volume
vol = Volume(volume)

# IsosurfaceBrowser(Plotter) instance:
plt = IsosurfaceBrowser(vol, use_gpu=True, c="gold")
plt.show(axes=7, bg2="lb")

# Get the isosurface value
iso_value = plt.sliders[0][0].value
plt.close()
printc(f"The selected iso value is {iso_value:2f}.", c="orange")

# Store the value
pipeline["ISOVAL"] = iso_value
dic2file(pipeline, pipeline_file)
