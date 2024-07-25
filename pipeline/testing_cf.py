import os
import sys

from utils import dic2file, file2dic, get_side_postion
from vedo import Text2D, Volume, printc
from vedo.applications import IsosurfaceBrowser

raw_volume = sys.argv[1]

# pipeline_file = os.path.join(folder, "pipeline.log")
# pipeline = file2dic(pipeline_file)
# volume = raw_volume.replace(".tif", ".vti")
# channel = os.path.basename(volume).split("_")[3].upper()
# volume = os.path.join(folder, os.path.basename(volume))

# sp = get_side_postion(raw_volume)

# # Ask the user if wants to do it again
# # if os.path.exists(volume) and pipeline.get(channel, False):
# #     print("This is already done!")
# #     sys.exit()

# sp = get_side_postion(raw_volume)
# if sp is not None:
#     side, position = sp

# Constants
# SPACING = (0.65, 0.65, 2)
SPACING = (1.14, 1.14, 5)
# SPACING = (1.14, 1.14, 2)
SIGMA = (6, 6, 6)
CUTOFF = 0.05
# SIZE = (1024, 1024, 296)  # high res
SIZE = (512, 512, 296)  # low res

# Read the volume and add spacing
vol = Volume(raw_volume)
vol.spacing(SPACING)

# plt = IsosurfaceBrowser(vol, use_gpu=True)
# plt.show()
# plt.close()

# exit()

# # Promp the user to pick up the low and high value for the clipping
plt = IsosurfaceBrowser(vol, use_gpu=True)
txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
plt += txt
txt.text("Pick the bottom isovalues")
plt.show()
v0 = int(plt.sliders[0][0].value)
txt.text("Now, select the top isovalue, please!")
plt.show()
v1 = int(plt.sliders[0][0].value)
printc(f"The isovalues are {v0}, and {v1}")

if v0 == v1:
    v1 += 1

# Apply the clip and resize
printc("-> Thresholding... within", (v0, v1))
vol = vol.cmap("Purples", vmin=v0, vmax=v1)
vol.threshold(below=v0, replace=0).threshold(above=v1, replace=v1)
vol.resize(SIZE)
side = "L"
# Mirror if the left so we can compare with Right reference
if side == "L":
    vol.mirror()

# Smooth the limb
vol.smooth_gaussian(sigma=SIGMA)
vol.frequency_pass_filter(high_cutoff=CUTOFF)

# Inspection
txt.text("Check everything is good...")
plt.show()
plt.close()

# printc("-> Writing the volume", volume)
volume = raw_volume.replace(".tif", ".vti")
vol.write(volume)

# volume = os.path.basename(volume)
# printc("-> Saving metadata")
# pipeline[channel] = volume
# pipeline["SIDE"] = side
# pipeline["POSITION"] = position
# pipeline[f"{channel}_v0"] = v0
# pipeline[f"{channel}_v1"] = v1
# dic2file(pipeline, pipeline_file)
