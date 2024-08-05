from vedo import Mesh, Plotter, Volume, settings

from limblab.utils import styles

fig2_camera_tilted_2 = dict(
    pos=(954.948, -1703.72, -2294.00),
    focal_point=(715.839, 714.045, 289.983),
    viewup=(-0.181888, 0.709569, -0.680756),
    roll=14.1133,
    distance=3546.79,
    clipping_range=(2171.66, 5286.34),
)

settings.screenshot_transparent_background = True


def main():

    channel = "Hoxa11/HCR11_HOXA11_l1_hoxa11_647_LH.vti"
    surface = "Hoxa11/HCR11_HOXA11_l1_dapi_488_LH_surface.vtk"

    # Load the channel
    channel = Volume(channel).isosurface(value=300).color(
        styles["channel_0"]["color"])
    limb = Mesh(surface).color(styles["limb"]["color"]).alpha(0.3)

    plt = Plotter(bg="white")

    plt.camera = fig2_camera_tilted_2

    plt.add((channel, limb))
    plt.show().freeze()
    plt.screenshot("figures/figure-2-panel-c.png")

    plt.remove((channel, limb))
    plt.add(limb.alpha(1).lw(2))
    plt.screenshot("figures/figure-2-panel-d.png")

    plt.close()


if __name__ == "__main__":
    main()
