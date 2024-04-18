# Same as warp4b.py but using the applications.MorphPlotter class
from vedo import Mesh, settings, dataurl, Plotter, grep
from vedo.applications import MorphPlotter


settings.default_font = "Calco"
settings.enable_default_mouse_callbacks = False

source = Mesh(dataurl + "limb_surface.vtk").color("k5")
source.rotate_y(90).rotate_z(-60).rotate_x(40)


target = (
    Mesh(dataurl + "290.vtk")
    .cut_with_plane(origin=(1, 0, 0))
    .rotate_y(-30)
    .color("yellow5")
)

plt = MorphPlotter(source, target, size=(2490, 850), axes=14)
plt.show()
plt.close()

plt.plot
