# Same as warp4b.py but using the applications.MorphPlotter class
from vedo import Mesh, settings, dataurl, grep
from vedo.applications import MorphPlotter
import os


def closest_value(input_list, target):
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest


# TODO: This should be the input
folder = "HCR12_8a_dapi_405"

# Get the paths
pipeline = os.path.join(folder, "pipeline.txt")
result = grep(pipeline, "STAGE")
stage = result[0][1]

surface = grep(pipeline, "SURFACE")[0][1]


reference_meshes = (250, 260, 270, 290)
reference_stage = closest_value(reference_meshes, int(stage))

print(reference_stage, stage)

settings.default_font = "Calco"
settings.enable_default_mouse_callbacks = False

source = Mesh(surface).color("k5")
# source.rotate_y(90).rotate_z(-60).rotate_x(40)


target = Mesh(dataurl + f"{reference_stage}.vtk").color("yellow5", 0.2)


plt = MorphPlotter(source, target, size=(2490, 850), axes=14)
plt.show()
# print(plt.warped.transform)
wrap_transform = plt.warped.transform
plt.close()

tname = "nonlinear_transformation.mat"
wrap_transform.write(os.path.join(folder, tname))
print(wrap_transform)

with open(pipeline, "a") as f:
    print("NONTRANS", os.path.join(folder, tname), file=f)
