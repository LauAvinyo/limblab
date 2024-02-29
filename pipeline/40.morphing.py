# Same as warp4b.py but using the applications.MorphPlotter class
import os
import sys

from utils import file2dic, closest_value, dic2file
from vedo import Mesh, dataurl, settings
from vedo.applications import MorphPlotter


if len(sys.argv) != 2:
    print("Usage: python script_name.py folder_name")
    sys.exit(1)

folder = sys.argv[1]

pipeline_file = os.path.join(folder, "pipeline.txt")
pipeline = file2dic(pipeline_file)
surface = pipeline["SURFACE"]
stage = pipeline["STAGE"]

# TODO: Use all the refeences!
reference_meshes = (250, 260, 270, 290)
reference_stage = closest_value(reference_meshes, int(stage))

print(reference_stage, stage)

settings.default_font = "Calco"
settings.enable_default_mouse_callbacks = False

source = Mesh(surface).color("k5")
# source.rotate_y(90).rotate_z(-60).rotate_x(40)

# TODO: Change is for the folder with all the meshes!
target = Mesh(dataurl + f"{reference_stage}.vtk").color("yellow5", 0.2)


plt = MorphPlotter(source, target, size=(2490, 850), axes=14)
plt.show()
# print(plt.warped.transform)
wrap_transform = plt.warped.transform
plt.close()

tname = surface.replace("_surface.vtk", ".mat")
wrap_transform.write(tname)
print(wrap_transform)

pipeline["TRANSFORMATION"] = tname
dic2file(pipeline, pipeline_file)
