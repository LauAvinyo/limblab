from vedo import dataurl, load, show, Volume, Text2D
from vedo.applications import IsosurfaceBrowser, Slicer3DPlotter
from vedo import Volume, show
import numpy as np

# Return a list of 2 meshes
# g = load(dataurl + "297.vtk")
# print(g)
# show(g)
# # Return a list of meshes by reading all files in a directory
# # (if directory contains DICOM files then a Volume is returned)
data_file = "HCR12_8a_sox9_594.tif"
# limb = Mesh(dataurl + "270.vtk").c("gold").decimate(n=100)
raw = Volume(data_file)

arr = raw.tonumpy()
arr[arr < 140] = 0

vol = Volume(arr)
vol.write("HCR12_8a_sox9_594_vol.tif")
