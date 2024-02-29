from vedo import (
    NonLinearTransform,
    Volume,
    TetMesh,
    Plane,
    show,
)
import os
import sys

# python 269 ddHCR12_8a_sox9_594.vti HCR12_8a_dapi_405/nonlinear_transformation.mat"

if len(sys.argv) != 4:
    print("Usage: python script_name.py stage volume t_path")
    sys.exit(1)

stage = sys.argv[1]
volume = sys.argv[2]
transformation = sys.argv[3]


# From the input we can get
tetmesh = f"/Users/lauavino/Desktop/medium_resolution/{stage}.vtu"
channel = os.path.basename(volume).split("_")[2]

# Read volume
vol = Volume(volume).resize([100, 100, 100])
T = NonLinearTransform(transformation)
T.update()
vol.apply_transform(T)

# Read the mesh
tetm = TetMesh(tetmesh)
plane = Plane(normal=(1, 0, 0)).pos([1, 0, 0])
tetm = tetm.cut_with_mesh(plane, invert=True, whole_cells=True)

# Extract the scalar field from the volumetric data into the tetmesh
tetm.interpolate_data_from(vol, n=4).cmap("viridis").alpha(0.2)
tetm.pointdata.rename("ImageScalars", "SOX9")
tetm.map_points_to_cells(["SOX9"])  # if needed

show([vol, tetm.alpha(0.5)], axes=14, viewup="z")
