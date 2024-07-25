import vedo

plt = vedo.Plotter(shape=(1, 3))

# p1 = "../data/HCR/HCR11_HOXA11_L1/HCR11_HOXA11_l1_hoxa11_647_LH.vti"
p1 = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/pipeline/HCR20_BMP2_l1/HCR20_BMP2_l1_bmp2_647_LF.vti"
m1 = vedo.Volume(p1).isosurface(value=640).color((176, 219, 67))
# .isosurface(value=286).extract_largest_region()

# p2 = "../data/HCR/HCR11_HOXA11_L1/HCR11_HOXA11_l1_hoxa13_546_LH.vti"
# m2 = vedo.Volume(p2).isosurface().extract_largest_region().color((219, 39, 99))

ps = "../data/HCR/HCR11_HOXA11_L1/HCR11_HOXA11_l1_dapi_488_LH_surface.vtk"
ps = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/pipeline/HCR20_BMP2_l1/HCR20_BMP2_l1_sox9_594_LF.vti"
m3 = vedo.Volume(ps).isosurface().extract_largest_region().color((219, 39, 99))

# m3 = vedo.Mesh(ps).color((252, 171, 16))  # .frontface_culling()

# plt += (m1, m2, m3)
plt.at(0).add(m1)
plt.at(1).add(m3)
plt.at(2).add((m1.alpha(0.5), m3))

plt.show(axes=14).interactive()

plt.close()
