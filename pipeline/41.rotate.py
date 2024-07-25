import os
import sys

from utils import (closest_value, dic2file, file2dic, get_reference_limb,
                   reference_stages)
from vedo import Mesh, Plotter, ask, printc, show

if len(sys.argv) != 2:
    print("Usage: python script_name.py folder_name")
    sys.exit(0)

folder = sys.argv[1]

pipeline_file = os.path.join(folder, "pipeline.log")
pipeline = file2dic(pipeline_file)
surface = pipeline.get("BLENDER", pipeline["SURFACE"])
stage = pipeline.get("STAGE", False)

print(surface, stage)

# side = pipeline.get("SIDE")

if not stage:
    print("Please run the staging algorithm first!")
    sys.exit(0)

# Get the target stage
reference_stage = closest_value(reference_stages, int(stage))
print(
    f"The stage of the limb is {stage} and we are using as reference {reference_stage}."
)
refence_limb = get_reference_limb(reference_stage)
print(f"The reference limb is in file {refence_limb}.")

# Get the Surfaces
surface = os.path.join(folder, surface)
source = Mesh(surface).color((252, 171, 16)).scale(1.1)
target = (
    Mesh(refence_limb).cut_with_plane(origin=(1, 0, 0))
    # .color("yellow5")
    .alpha(0.5).color((43, 158, 179)))

printc("Manually align mesh by toggling 'a'", invert=True)
# show(, axes=14).close()

# Store the Transformation
T = source.apply_transform_from_actor()
tname = surface.replace("_surface.vtk", "_rotation.mat")
# if os.path.isfile(tname):
#     answer = ask("Overwrite existing transformation matrix? (y/N)", c="y")
#     if answer == "y":
#         # T.filename = tname
#         T.write(os.path.join(folder, tname))
#         print(T)
# else:
#     print("Saving!")
#     T.write(os.path.join(folder, tname))
#     print(T)

plt = Plotter(shape="1|2", sharecam=False)

plt.at(2).camera = dict(
    position=(727.482, -9177.46, 178.073),
    focal_point=(727.482, 387.830, 178.073),
    viewup=(2.82523e-34, -2.37707e-17, 1.00000),
    roll=1.61874e-32,
    distance=9565.29,
    clipping_range=(7962.46, 11606.0),
)

plt.at(1).camera = dict(
    position=(727.482, 387.830, 9725.70),
    focal_point=(727.482, 387.830, 178.073),
    viewup=(0, 1.00000, 0),
    roll=0,
    distance=9547.62,
    clipping_range=(8305.31, 11134.5),
)

# plt.at(2).freeze()

plt.at(2).add(source.alpha(0.4), target.alpha(0.6))
plt.at(1).add(source.alpha(0.4), target.alpha(0.6))
plt.at(0).add(source.alpha(0.4), target.alpha(0.6))

# plt.at(2).freeze()

plt.show(axes=14).interactive()
plt.close()
# # print(plt.warped.transform)
# T = source.transform
# print(T)
# T.write(tname)
# plt.close()

# pipeline["TRANSFORMATION"] = os.path.basename(tname)
# pipeline["ROTATION"] = os.path.basename(tname)
# dic2file(pipeline, pipeline_file)
