from vedo import dataurl, Mesh, show, Volume, Text2D, LinearTransform
from vedo.applications import IsosurfaceBrowser, Slicer3DPlotter

# from vedo import *

print(dataurl)
# Return a list of 2 meshes
g = Mesh(dataurl + "270.vtk").pickable(False).print()
vol = (
    Volume("HCR12_8a_sox9_594_vol.tif")
    .print()
    .spacing((0.65, 0.65, 2))
    .resize(296, 296, 296)
)
surface = (vol.isosurface(50).extract_largest_region()).mirror()

show(surface, g, axes=1)

M = surface.actor.GetMatrix()
T = LinearTransform(M)
T.write("mytransf.mat")
surface.apply_transform(M)
# surface.actor.PokeMatrix()

surface.write("HCR12_8a_sox9_594_decimated.vtk")
surface.align_to(g, invert=0, use_centroids=True)
show(surface, g, axes=1)
