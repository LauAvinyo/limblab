from vedo import *

limb0 = Mesh("data/example_meshes/meshed_260.vtk")
limb0 = CellCenters(limb0)
limb0.add_ids()

limb1 = Mesh("data/example_meshes/meshed_261.vtk").print()
limb1.add_ids()

arr = np.zeros(limb0.npoints)
arr[7650] = 1
limb0.pointdata["scalar"] = arr
limb0.cmap("viridis", vmin=0, vmax=1)

limb1.interpolate_data_from(limb0, n=3)
limb1.cmap("viridis", vmin=0, vmax=1)
limb1.map_points_to_cells()

print(np.unique(limb1.celldata["scalar"]))
print(limb1)

show(limb0, limb1, N=2, axes=1)
