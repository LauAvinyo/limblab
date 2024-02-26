import json
import os

from utils import get_integer_basename
from vedo import CellCenters, NonLinearTransform, TetMesh, np

# TODO: Pass this as arguments
t_folder = "/Users/lauavino/Documents/PhD/code/sharpe/TOPSECRET/interpolation_map/transformations"
folder = "/Users/lauavino/Desktop/tet_meshes_medium/"

# List all files in the folder
files = os.listdir(folder)

# Filter out only files (excluding directories)
files = [
    f for f in files if os.path.isfile(os.path.join(folder, f)) and f != ".DS_Store"
]


# Sort the files based on their integer basename
files_sorted = sorted(files, key=get_integer_basename)

fmap = {}

# Iterate through the sorted files and their next file
for current_file, next_file in zip(files_sorted, files_sorted[1:] + [None]):
    current_file_path = os.path.join(folder, current_file)

    if next_file:
        next_file_path = os.path.join(folder, next_file)
    else:
        break

    print("Current file:", current_file_path, sep="\t")
    print("Next file:", next_file_path, sep="\t")

    t0 = current_file.split(".")[0]
    t1 = next_file.split(".")[0]
    fmap[f"{t0}-{t1}"] = {}

    limb0 = TetMesh(current_file_path)
    limb1 = TetMesh(next_file_path)

    # exit()

    # Apply the streching to the limb0
    tname = current_file.replace(".vtu", ".mat")
    T = NonLinearTransform(os.path.join(t_folder, tname))
    limb0.apply_transform(T)

    # Use the centers of the tetrahedron
    limb0 = CellCenters(limb0)
    limb1 = CellCenters(limb1)
    climb1 = limb1.clone()

    # Loop though all points
    for i in range(limb0.npoints):
        if i % 100 == 0:
            print(f"i = {i} of {limb0.npoints}. {(i/limb0.npoints * 100):.2f}% done")

        # Set the scalars of limb0 to 0 except a particular point
        arr = np.zeros(limb0.npoints)
        arr[i] = 1
        limb0.pointdata["scalar"] = arr

        limb1 = CellCenters(limb1)
        limb1.interpolate_data_from(limb0, n=3)
        limb1.map_points_to_cells()

        # Find the indices where the values are not zero
        idxs = np.where(limb1.celldata["scalar"] != 0)[0]

        # Store it on the fmap
        fmap[f"{t0}-{t1}"][i] = dict(
            (int(i), float(limb1.celldata["scalar"][i])) for i in idxs
        )

        # TODO: This is for sure not the way to go!
        limb1 = climb1

    print("--------")

    # break

print(fmap.keys())
with open("testing.json", "w") as f:
    json.dump(fmap, f)

    # show(limb0, limb1, N=2, axes=1)
