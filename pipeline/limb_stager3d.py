import numpy as np
from vedo import settings, dataurl, fit_plane, printc, vector, grep
from vedo import Mesh, Points, Axes, Text2D, LinearTransform
from vedo.applications import SplinePlotter
import os

# TODO:
# - [ ] Get the lines and add it onto the

# TODO: Set this as arguments!
limbstager_exe = (
    "/Users/lauavino/Documents/PhD/code/sharpe/TOPSECRET/limb-stagig/src/limbstager"
)

limbstager_file = ".tmp_staging_file.txt"
outfile = ".tmp_out_file.txt"
pipeline_file = "./pipeline_file.txt"


def compute_rotation_matrix_to_align(v, target=(0, 0, 1)):
    v_normalized = v / np.linalg.norm(v)
    target = -np.array(target) / np.linalg.norm(target)
    axis = np.cross(v_normalized, target)
    if np.linalg.norm(axis) == 0:
        if v_normalized[2] == -1:
            # 180 degrees rotation around any horizontal axis
            axis = np.array([1, 0, 0])
            theta = np.pi
        else:
            return np.identity(3)  # no rotation needed
    axis_normalized = axis / np.linalg.norm(axis)
    cos_theta = np.dot(v_normalized, target)
    theta = np.arccos(cos_theta)
    K = np.array(
        [  # Rodrigues' rotation
            [0, -axis_normalized[2], axis_normalized[1]],
            [axis_normalized[2], 0, -axis_normalized[0]],
            [-axis_normalized[1], axis_normalized[0], 0],
        ]
    )
    identity_matrix = np.identity(3)
    return identity_matrix + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


def kfunc(event):
    if event.keypress == "s":
        if plt.line:
            plane = fit_plane(plt.cpoints)
            matrix = compute_rotation_matrix_to_align(plane.normal)
            T = LinearTransform(matrix)
            fitpoints = Points(plt.cpoints, c="red5", r=10).pickable(0)
            fitpoints.apply_transform(T).project_on_plane("z").alpha(1)
            fitpoints.name = "Fit"
            fitline = plt.line.clone()
            fitline.apply_transform(T).project_on_plane("z").alpha(1)
            fitline.name = "Fit"
            axes = Axes(fitline, c="k")
            axes.name = "Fit"
            plt.at(1).remove("Fit").add(fitpoints, fitline, axes)
            plt.at(1).reset_camera()
            plt.at(0)  # focus back on the mesh renderer
            # stage the limb
            txt.text("Staging your limb, please wait...")
            if os.path.isfile(limbstager_exe):
                # create an output file to feed the staging system executable
                with open(outfile, "w") as f:
                    f.write(
                        f"gene_mapper {outfile}  u 1.0  0 0 0 0 {len(fitpoints.coordinates)}\n"
                    )
                    for p in vector(fitpoints.coordinates):
                        f.write(f"MEASURED {p[0]} {p[1]}\n")

                # now stage: a .tmp_out.txt file is created
                errnr = os.system(
                    f"{limbstager_exe} {outfile} > .tmp_out.txt 2> /dev/null"
                )
                if errnr:
                    printc(
                        f"limbstager executable {limbstager_exe} returned error:",
                        errnr,
                        c="r",
                    )
                    return
            else:
                printc("INFO: limbstager executable not found.", c="lg")
                return

            plt.render()

            # print(fitpoints.coordinates)
            # ...

            print("Reasing the grep!")
            result = grep(".tmp_out.txt", "RESULT")
            if not len(result):
                printc("Error - Could not stage the limb, RESULT tag is missing", c="r")
                return
            stage = result[0][1]
            with open(pipeline_file, "w") as f:
                print("stage", stage, sep="\t", file=f)
            txt.text(f"Limb staged as {stage}")
            plt.render()
    elif event.keypress == "r":
        plt.reset_camera().render()
    elif event.keypress == "q":
        plt.close()


settings.use_depth_peeling = True
settings.enable_default_keyboard_callbacks = False
settings.default_font = "Dalim"

# load a 3D mesh of the limb to stage
example_mesh = (
    "/Users/lauavino/Documents/PhD/code/sharpe/TOPSECRET/useful_scripts/297.vtk"
)
msh = Mesh(example_mesh).c("blue8", 0.8)
txt = Text2D(pos="top-center", bg="yellow5", s=1.5)

plt = SplinePlotter(msh, title="3D Stager", N=2, sharecam=0, size=(2000, 1000), axes=14)
plt.verbose = False
plt.instructions.text(
    (
        "Click to add a point\n"
        "Right-click to remove it\n"
        "Press c to clear points\n"
        "Press s to stage the limb\n"
        "Press r to reset camera\n"
        "Press q to quit"
    )
)
plt.add_callback("on keypress", kfunc)
plt.at(0).add(Axes(msh, c="k", xygrid=False, ztitle=" "))
plt.at(1).add(txt)
plt.at(0).show(interactive=True)
