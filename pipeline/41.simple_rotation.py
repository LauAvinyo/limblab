import os
import sys

from utils import (
    closest_value,
    dic2file,
    file2dic,
    get_reference_limb,
    reference_stages,
)
from vedo import Mesh, ask, printc, show

if len(sys.argv) != 2:
    print("Usage: python script_name.py folder_name")
    sys.exit(0)

folder = sys.argv[1]

pipeline_file = os.path.join(folder, "pipeline.txt")
pipeline = file2dic(pipeline_file)
surface = pipeline["SURFACE"]
stage = pipeline.get("STAGE", False)

if not stage:
    print("Please run the staging algorithm first!")
    sys.exit(0)

# Get the target stage
reference_stage = closest_value(reference_stages, int(stage))
print(f"The stage of the limb is {stage} and we are using as reference {reference_stage}.")
refence_limb = get_reference_limb(stage)
print(f"The reference limb is in file {refence_limb}.")

# Get the Surfaces
source = Mesh(surface)
target = (
    Mesh(refence_limb)
    .cut_with_plane(origin=(1, 0, 0))
    .color("yellow5")
)

printc("Manually align mesh by toggling 'a'", invert=True)
show(source, target, axes=14).close()


# Store the Transformation
T = source.apply_transform_from_actor()
tname = surface.replace("_surface.vtk", "_rotation.mat")
if os.path.isfile(tname):
    answer = ask("Overwrite existing transformation matrix? (y/N)", c="y")
    if answer == "y":
        # T.filename = tname
        T.write(os.path.join(folder, tname))
        print(T)
else:
    T.write(os.path.join(folder, tname))
    print(T)


pipeline["TRANSFORMATION"] = tname
dic2file(pipeline, pipeline_file)

pipeline["ROTATION"] = tname
dic2file(pipeline, pipeline_file)
