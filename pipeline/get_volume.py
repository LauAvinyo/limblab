import os

from vedo import Volume, printc
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

# TODO: Get it from input
# Read the volume path
filename = "../data/HCR/HCR12_8a_dapi_405.tif"
folder = "HCR12_8a_dapi_405"
pipeline = os.path.join(folder, "pipeline.txt")


side = "L"  # Left or Right limb
iso_value = 0  # isosurface value, 0=automatic
spacing = (0.65, 0.65, 2)
# size    = (1024, 1024, 296)  # high res
size = (512, 512, 296)  # low res
clip_range = (60, 600)


volume_path = filename.replace(".tif", ".vti")

if os.path.exists(volume_path):  # load existing volume
    print("This is already done!")
    # TODO: Ask if they want to run it!
    exit()

v0, v1 = clip_range
vol = Volume(filename).spacing(spacing).cmap("Paired", vmin=v0, vmax=v1)
h = histogram(vol, bins=75, logscale=1, max_entries=1e5, c="Paired")
plt = IsosurfaceBrowser(vol, scalar_range=clip_range, use_gpu=True)
plt.add([filename, h.clone2d(size=0.7)])
# plt.show(axes=14).close()  # inspect it
printc("-> Thresholding... within", clip_range)
vol.threshold(below=v0, replace=0).threshold(above=v1, replace=v1)
vol.resize(size)
h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
if side == "L":  # mirror volume to match the Right reference
    vol.mirror()
printc("-> Writing resized volume", volume_path)
vol.write(volume_path)

with open(pipeline, "a") as f:
    print("VOLUME", volume_path, file=f)
