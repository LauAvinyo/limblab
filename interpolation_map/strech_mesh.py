from vedo import TetMesh, Lines, NonLinearTransform, show

import os


output_folder = "/Users/lauavino/Documents/PhD/code/sharpe/TOPSECRET/interpolation_map/transformations"
# Define the folder path
folder = "/Users/lauavino/Desktop/tet_meshes_medium/"


# List all files in the folder
files = os.listdir(folder)

# Filter out only files (excluding directories)
files = [
    f for f in files if os.path.isfile(os.path.join(folder, f)) and f != ".DS_Store"
]


# Define a function to extract the basename (integer part)
def get_integer_basename(filename):
    basename, _ = os.path.splitext(filename)
    try:
        return int(basename)
    except ValueError:
        return None


# Sort the files based on their integer basename
files_sorted = sorted(files, key=get_integer_basename)

# Iterate through the sorted files and their next file
for current_file, next_file in zip(files_sorted, files_sorted[1:] + [None]):
    current_file_path = os.path.join(folder, current_file)

    if next_file:
        next_file_path = os.path.join(folder, next_file)
    else:
        break

    # Do whatever you want with the current and next files
    print("Current file:", current_file_path, sep="\t")
    print("Next file:", next_file_path, sep="\t")

    tlimb0 = TetMesh(current_file_path)
    tlimb1 = TetMesh(next_file_path)

    mlimb0 = tlimb0.tomesh().color("green3")
    mlimb1 = tlimb1.tomesh().color("blue5").alpha(0.4)

    mlimb0_t = mlimb0.clone()

    mlimb0.cut_with_plane(origin=(10, 0, 0))
    mlimb1.cut_with_plane(origin=(10, 0, 0))

    mlimb0.subsample(0.025)

    targets = []
    sources = mlimb0.vertices
    for pt in sources:
        cp = mlimb1.closest_point(pt)
        targets.append(cp)

    lines = Lines(sources, targets, lw=3)

    T = NonLinearTransform()
    T.source_points = sources
    T.target_points = targets
    tname = current_file.replace(".vtu", ".mat")
    T.write(os.path.join(output_folder, tname))

    # tlimb0.apply_transform(T)
    # show(mlimb0, lines, mlimb0_t, mlimb1.wireframe(), axes=1)

    print("----------")
