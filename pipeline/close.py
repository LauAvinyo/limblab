from vedo import Mesh, show, dataurl
a = Mesh("/Users/lauavino/Documents/Code/limb-hcr-pipeline/data/HCR/HCR12_FZD7_L1/HCR12_FZD7_L1_dapi_405_RF_surface_blender_open.vtk").lw(1).bc('red')

b = a.clone()  # make a copy
b.fill_holes().color("lb").bc('red5')

show(a, b, __doc__, elevation=-40).close()
