"""Interactively cut a mesh by drawing free-hand a spline in space"""
# The tool can also be invoked from command line e.g.: > vedo --edit mesh.ply
import vedo
from vedo.applications import FreeHandCutPlotter
import sys
from utils import file2dic
import os
from vedo.applications import IsosurfaceBrowser


if len(sys.argv) != 3:
    print("Usage: python script_name.py folder_name channel")
    sys.exit(1)
folder = sys.argv[1]
channel = sys.argv[2]


# Get the paths
pipeline_file = os.path.join(folder, "pipeline.log")
pipeline = file2dic(pipeline_file)
path = pipeline[channel.upper()]
surface = path.replace(".vti", "_surface.vtk")
print(path)
vol = vedo.Volume(path).color('gold', 0.25)  # Mesh

msh = vedo.Mesh(surface)

plt = IsosurfaceBrowser(vol.alpha(0.5), use_gpu=True, alpha=0.5)
# txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
# plt += txt
# txt.text("Pick the bottom isovalues")
plt += msh.alpha(0.5).color("green")
plt.show()

# Do the cutting
v0 = int(plt.sliders[0][0].value)
plt.close()


cutting_surface = vol.isosurface(v0)

# make a working copy and cut it with the ellipsoid
cut_iso = msh.clone().cut_with_mesh(cutting_surface).c("gold").bc("t")

plt = vedo.Plotter(axes=14)
plt.show(viewup="z")

# plt.init(some_list_of_initial_pts) #optional!
plt.close()
