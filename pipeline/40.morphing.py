# Same as warp4b.py but using the applications.MorphPlotter class
import os
import sys

from utils import closest_value, dic2file, file2dic, reference_stages
from vedo import Mesh, dataurl, settings
from vedo.applications import MorphPlotter

if len(sys.argv) != 2:
    print("Usage: python script_name.py folder_name")
    sys.exit(1)

folder = sys.argv[1]

pipeline_file = os.path.join(folder, "pipeline.log")
pipeline = file2dic(pipeline_file)
surface = os.path.join(folder, pipeline["SURFACE"])
stage = pipeline.get("STAGE", False)

if not stage:
    print("Please run the staging algorithm first!")
    exit()

reference_stage = closest_value(reference_stages, int(stage))

print(reference_stage, stage)

settings.default_font = "Calco"
settings.enable_default_mouse_callbacks = False

source = Mesh(surface).color("k5")
# source.rotate_y(90).rotate_z(-60).rotate_x(40)

target = Mesh(dataurl + f"{270}.vtk").color("yellow5", 0.8)

plt = MorphPlotter(source, target, axes=14)
plt.show()
# print(plt.warped.transform)
wrap_transform = plt.warped.transform
plt.close()

tname = surface.replace("_surface.vtk", "_morphing.mat")
wrap_transform.write(tname)
print(wrap_transform)

pipeline["TRANSFORMATION"] = tname
pipeline["MORPHING"] = tname
dic2file(pipeline, pipeline_file)
