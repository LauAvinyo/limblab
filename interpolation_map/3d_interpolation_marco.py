import os
import json
import numpy as np
from vedo import CellCenters, NonLinearTransform, TetMesh, show
from vedo.utils import humansort, progressbar

# TODO: Pass this as arguments
t_folder = "transformations"
folder = "/home/musy/Projects/data/clonal/meshes_tetras/medium_resolution/"

# Filter out only files (excluding directories)
files = os.listdir(folder)
files_sorted = humansort([
    f for f in files if os.path.isfile(os.path.join(folder, f)) and f != ".DS_Store"
])

# Iterate through the sorted files and their next file
fmap = {}
for current_file, next_file in zip(files_sorted, files_sorted[1:] + [None]):
    current_file_path = os.path.join(folder, current_file)

    if next_file:
        next_file_path = os.path.join(folder, next_file)
    else:
        break

    age = int(os.path.basename(current_file).split(".")[0])
    # if not 250 <= age <= 251: continue # for testing

    t0 = current_file.split(".")[0]
    t1 = next_file.split(".")[0]
    fmap[f"{t0}-{t1}"] = []

    limb0 = TetMesh(current_file_path)
    limb1 = TetMesh(next_file_path)

    # Apply the streching to the limb0
    T = NonLinearTransform(os.path.join(t_folder, f"{age}.mat"))
    limb0.apply_transform(T)

    # Use the centers of the tetrahedron
    limb0 = CellCenters(limb0)
    limb1 = CellCenters(limb1)

    # Loop though all points
    n0 = limb0.npoints
    for i in progressbar(n0, title=f"Loop through points in limb {age}h"):

        # Set the scalars of limb0 to 0 except at point i
        arr0 = np.zeros(n0).astype(float)
        arr0[i] = 1.0
        limb0.pointdata["scalar"] = arr0

        limb1c = limb1.clone().interpolate_data_from(limb0, n=3)
        arr1 = limb1c.pointdata["scalar"]

        # Find the indices where the values are not zero
        ids = np.where(arr1 != 0)[0]

        # Store it on the fmap
        fmap[f"{t0}-{t1}"].append([(i, arr1[k]) for k in ids])

with open("testing.json", "w") as f:
    print(fmap.keys())
    json.dump(fmap, f)
    # show(limb0, limb1, N=2, axes=1)
