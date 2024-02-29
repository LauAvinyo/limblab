import os

from vedo import Mesh, ask, dataurl, printc, show, grep, NonLinearTransform


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

################################################

# Get the the data from the pipeline file
pipeline = os.path.join(folder, "pipeline.txt")
surface = grep(pipeline, "SURFACE")[0][1]
stage = int(grep(pipeline, "STAGE")[0][1])

reference_meshes = (250, 260, 270, 290)
reference_stage = closest_value(reference_meshes, int(stage))

print(reference_stage, stage)


# Apply non linear tranformation
source = Mesh(surface)
tname = os.path.join(folder, "nonlinear_transformation.mat")
T = NonLinearTransform(tname)
T.update()
source.apply_transform(T)

target = (
    Mesh(dataurl + f"{reference_stage}.vtk")
    .cut_with_plane(origin=(1, 0, 0))
    .color("yellow5")
)

printc("Manually align mesh by toggling 'a'", invert=True)
show(source, target, axes=14).close()

# ############################################### save stuff
T = source.apply_transform_from_actor()
tname = "linear_transformation.mat"
if os.path.isfile(tname):
    answer = ask("Overwrite existing transformation matrix? (y/N)", c="y")
    if answer == "y":
        # T.filename = tname
        T.write(os.path.join(folder, tname))
        print(T)
else:
    T.write(os.path.join(folder, tname))
    print(T)


with open(pipeline, "a") as f:
    print("LINTRANS", os.path.join(folder, tname), file=f)
