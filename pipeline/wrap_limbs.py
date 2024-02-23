# Same as warp4b.py but using the applications.MorphPlotter class
from vedo import Mesh, settings, dataurl, Plotter, grep
from vedo.applications import MorphPlotter


def closest_value(input_list, target):
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest


pipeline_file = "./pipeline_file.txt"
result = grep(pipeline_file, "stage")
stage = result[0][1]


reference_meshes = (250, 260, 270, 290)
reference = closest_value(reference_meshes, int(stage))

print(reference, stage)

settings.default_font = "Calco"
settings.enable_default_mouse_callbacks = False

source = Mesh(dataurl + "limb_surface.vtk").color("k5")
source.rotate_y(90).rotate_z(-60).rotate_x(40)


target = (
    Mesh(dataurl + f"{reference}.vtk").cut_with_plane(origin=(1, 0, 0))
    # .rotate_y(-30)
    .color("yellow5")
)

plt = MorphPlotter(source, target, size=(2490, 850), axes=14)
plt.show()
# print(plt.warped.transform)
wrap_transform = plt.warped.transform
plt.close()

tname = "transformation.mat"
wrap_transform.write(tname)
print(wrap_transform)
