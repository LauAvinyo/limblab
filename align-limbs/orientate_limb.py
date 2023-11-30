from vedo import Axes, Mesh, dataurl, printc, settings, show

settings.default_font = "Calco"

################################################
refname = dataurl + "270.vtk"


refmesh = Mesh(refname)  # .pickable(False)
vaxes = Axes(refmesh, xygrid=False)
printc("Manually align mesh by toggling 'a'", invert=True)
show(refmesh, vaxes, axes=14).close()
refmesh.apply_transform_from_actor()
refmesh.write("../data/reference_mesh_270.vtk")
