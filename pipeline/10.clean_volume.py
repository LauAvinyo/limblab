import os
import sys

from utils import dic2file, file2dic, get_side_postion
from vedo import Volume, printc
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

if len(sys.argv) != 3:
    print("Usage: python script_name.py folder_name volume_to_clean")
    sys.exit(1)

folder = sys.argv[1]
raw_volume = sys.argv[2]

pipeline_file = os.path.join(folder, "pipeline.txt")
pipeline = file2dic(pipeline_file)
volume = raw_volume.replace(".tif", ".vti")
channel = os.path.basename(volume).split("_")[2].upper()


sp = get_side_postion(volume)
if sp is not None:
    side, position = sp


spacing = (0.65, 0.65, 2)
# size    = (1024, 1024, 296)  # high res
size = (512, 512, 296)  # low res
clip_range = (60, 600)


if os.path.exists(volume) and pipeline.get(channel, False):
    print("This is already done!")
    sys.exit()

v0, v1 = clip_range
vol = Volume(raw_volume).spacing(spacing).cmap("Paired", vmin=v0, vmax=v1)
h = histogram(vol, bins=75, logscale=1, max_entries=1e5, c="Paired")
plt = IsosurfaceBrowser(vol, scalar_range=clip_range, use_gpu=True)
plt.add([vol, h.clone2d(size=0.7)])
# plt.show(axes=14).close()  # inspect it
printc("-> Thresholding... within", clip_range)
vol.threshold(below=v0, replace=0).threshold(above=v1, replace=v1)
vol.resize(size)
h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
if side == "L":  # mirror base to match the Right reference
    vol.mirror()


printc("-> Writing resized volume", volume)
vol.write(volume)

pipeline[channel] = volume
pipeline["SIDE"] = side
pipeline["POSITION"] = position
dic2file(pipeline, pipeline_file)
