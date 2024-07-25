import vedo
from utils import styles

plt = vedo.Plotter()

p2 = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/data/HCR20_BMP2_l1/HCR20_BMP2_l1_sox9_594_LF.vti"
m2 = vedo.Volume(p2).isosurface().extract_largest_region().color(
    styles[0][0]).lw(1).decimate(0.01).compute_normals().smooth()

ps = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/data/HCR20_BMP2_l1/HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk"
# ps = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/pipeline/HCR20_BMP2_l1/HCR20_BMP2_l1_sox9_594_LF.vti"
m3 = vedo.Mesh(ps).color(styles["limb"]["color"]).alpha(
    styles["limb"]["alpha"])

# m3 = vedo.Mesh(ps).color((252, 171, 16))  # .frontface_culling()
silh = m3.silhouette()
plt += silh

plt += (m2, m3)

plt.show(axes=14).interactive()

plt.close()
