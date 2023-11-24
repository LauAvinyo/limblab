import os

from vedo import Mesh, Volume, ask, dataurl, printc, settings, show
from vedo.applications import IsosurfaceBrowser
from vedo.pyplot import histogram

################################################
refname = dataurl + "270.vtk"
filename = "HCR12_8a_sox9_594.tif"
side = "L"  # Left or Right limb
iso_value = 0  # isosurface value, 0=automatic
spacing = (0.65, 0.65, 2)
# size    = (1024, 1024, 296)  # high res
size = (512, 512, 296)  # low res
clip_range = (60, 600)
data_path = '../data/HCR'

################################################
settings.default_font = "Calco"

basename = os.path.join(
    data_path, 
    os.path.basename(filename).replace(".tif", ".vti")
)

if os.path.exists(basename):  # load existing volume
    vol = Volume(basename)
    h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
else:  # create new volume from tif and save it
    v0, v1 = clip_range
    vol = Volume(filename).spacing(spacing).cmap("Paired", vmin=v0, vmax=v1)
    h = histogram(vol, bins=75, logscale=1, max_entries=1e5, c="Paired")
    plt = IsosurfaceBrowser(vol, scalar_range=clip_range, use_gpu=True)
    plt.add([filename, h.clone2d(scale=0.7)]).show(axes=14).close()  # inspect it
    printc("-> Thresholding... within", clip_range)
    vol.threshold(below=v0, replace=0).threshold(above=v1, replace=v1)
    vol.resize(size)
    h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
    if side == "L":  # mirror volume to match the Right reference
        vol.mirror()
    printc("-> Writing resized volume", basename)
    vol.write(basename)

if not iso_value:
    iso_value = h.mean
print(vol)
printc("-> Computing isosurface... iso_value =", iso_value)
surface = vol.isosurface(iso_value).extract_largest_region()

printc("-> Decimating isosurface... from n =", surface.npoints, "please wait...")
surface.decimate(0.1)

refmesh = Mesh(refname).pickable(False)

printc("Manually align mesh by toggling 'a'", invert=True)
show(surface, refmesh, axes=1).close()

# ############################################### save stuff
T = surface.apply_transform_from_actor()
tname = basename.replace(".vti", ".mat")
if os.path.isfile(tname):
    answer = ask("Overwrite existing transformation matrix? (y/N)", c="y")
    if answer == "y":
        # T.filename = tname
        T.write(tname)
        print(T)
else:
    T.write(tname)
    print(T)

printc("-> Writing", basename.replace(".vti", "_surface.vtk"))
surface.write(basename.replace(".vti", "_surface.vtk"))
show(surface, refmesh, axes=1)
