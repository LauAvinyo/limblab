import os

from vedo import (
    NonLinearTransform,
    Mesh,
    Volume,
    printc,
    TetMesh,
    np,
    show,
)


stage = 268
tetmesh_path = f"/Users/lauavino/Desktop/medium_resolution/{stage}.vtu"
volume_path = "../data/HCR/HCR12_8a_dapi_405.vti"
t_path = "HCR12_8a_dapi_405/nonlinear_transformation.mat"

# Read volume
if os.path.exists(volume_path):  # load existing volume
    vol = Volume(volume_path).resize([100, 100, 100])
else:
    printc("Run the first algorithm!")
    exit()


# Apply non linear tranformation

T = NonLinearTransform(t_path)
T.update()
vol.apply_transform(T)


tetra_mesh = TetMesh(tetmesh_path)

for i in range(tetra_mesh.ncells):

    # Get i tetrahedron
    vertices = tetra_mesh.cells[i]
    points = np.array([tetra_mesh.vertices[vertice] for vertice in vertices])
    faces = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
    tetrahedron = Mesh([points, faces])

    # Cut the volume (but cutting its points with a mesh)
    vol_points = vol.topoints()
    cut_points = vol_points.cut_with_mesh(tetrahedron)
    cut_volume = cut_points.tovolume()

    show(tetrahedron.color("green2"), cut_volume, axes=14).close()

    break

# plt = Plotter()

# plt += vol
# plt += tetmesh


# plt.show(axes=14, zoom=1.5).close()
