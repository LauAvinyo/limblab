import os
import sys

import requests
import vedo
from vedo import (Axes, LinearTransform, Mesh, Plotter, Points, Text2D, Volume,
                  fit_plane, grep, printc, settings, vector)
from vedo.applications import IsosurfaceBrowser, MorphPlotter, SplinePlotter
from vedo.pyplot import histogram

# from limblab.cameras_figures import (fig2_camera_side, fig2_camera_tilted,
#                                      fig2_camera_top)
from limblab.utils import (closest_value, dic2file, file2dic,
                           get_reference_limb, load_pipeline, reference_stages)

# from limblab.utils import styles

vedo.settings.screenshot_transparent_background = True
VERBOSE = True

# TODO:
LIMBSTAGER_EXE = "/Users/lauavino/Documents/Code/limblab/limb-staging/src/limbstager"


def _clean_volume(experiment_folder_path, raw_volume, channel, verbose=True):
    print(experiment_folder_path, raw_volume)

    channel = channel.upper()

    volume = os.path.join(experiment_folder_path,
                          os.path.basename(raw_volume).replace(".tif", ".vti"))

    # Read the pipeline
    pipeline = load_pipeline(experiment_folder_path)

    # # Figure setting
    # figures_path = "figures"
    # if "dapi" in str(raw_volume):
    #     color = styles["limb"]["color"]
    #     panel = "a"
    #     isovalue = 222
    #     v0, v1 = 240, 342
    # else:
    #     color = styles["channel_0"]["color"]
    #     panel = "b"
    #     isovalue = 290
    #     v0, v1 = 250, 560

    SIDE = pipeline["SIDE"]
    SPACING = list(float(i) for i in pipeline["SPACING"].split())
    print(SPACING)

    SIGMA = (6, 6, 6)
    CUTOFF = 0.05
    SIZE = (512, 512, 296)  # low res
    # SIZE = (1024, 1024, 296)  # high res

    # Read the Volume
    vol = Volume(str(raw_volume))

    # # FIGURE fig:clean Panels 1-3
    # # The commented code was used to do figure
    # # Uncomment to replicate the panels
    # _plt = Plotter(bg="white")
    # _plt.add(vol.isosurface(isovalue).color(color))
    # _plt.camera = fig2_camera_tilted
    # _plt.show(interactive=False)
    # _plt.screenshot(f"figures/figure-2-panel-{panel}1_tilted.png")
    # _plt.camera = fig2_camera_top
    # _plt.show()
    # _plt.screenshot(f"figures/figure-2-panel-{panel}1_top.png")
    # _plt.camera = fig2_camera_side
    # _plt.show()
    # _plt.screenshot(f"figures/figure-2-panel-{panel}1_side.png")
    # _plt.close()
    # ########

    # Add the specing to the volume
    vol.spacing(SPACING)

    # # FIGURE fig:clean:
    # # The commented code was used to do figure
    # # Uncomment to replicate the pane
    # _plt = Plotter(bg="white")
    # _plt.add(vol.isosurface(isovalue).color(color))
    # _plt.camera = fig2_camera_tilted
    # _plt.show(interactive=False)
    # _plt.screenshot(f"figures/figure-2-panel-{panel}2_tilted.png")
    # _plt.camera = fig2_camera_top
    # _plt.show()
    # _plt.screenshot(f"figures/figure-2-panel-{panel}2_top.png")
    # _plt.camera = fig2_camera_side
    # _plt.show()
    # _plt.screenshot(f"figures/figure-2-panel-{panel}2_side.png")
    # _plt.close()
    # ########

    #  Promp the user to pick up the low and high value for the clipping
    plt = IsosurfaceBrowser(vol, use_gpu=True, bg="white")
    txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
    plt += txt
    txt.text("Pick the bottom isovalues. Press q to continue.")
    plt.show()
    v0 = int(plt.sliders[0][0].value)
    txt.text("Now, select the top isovalue, please!")
    plt.show()
    v1 = int(plt.sliders[0][0].value)
    printc(f"The isovalues are {v0}, and {v1}")

    if v0 == v1:
        v1 += 1

    # Apply the clip and resize
    printc("-> Thresholding... within", (v0, v1))
    vol = vol.cmap("Purples", vmin=v0, vmax=v1)
    vol.threshold(below=v0, replace=0).threshold(above=v1, replace=v1)
    vol.resize(SIZE)

    # Mirror if the left so we can compare with Right reference
    if SIDE == "L":
        vol.mirror()

    # Smooth the limb
    printc("-> Apply smooth gaussian and low frequency filter...")
    vol.smooth_gaussian(sigma=SIGMA)
    vol.frequency_pass_filter(high_cutoff=CUTOFF)

    # # FIGURE fig:clean:
    # # The commented code was used to do figure
    # # Uncomment to replicate the panels
    # _plt = Plotter(bg="white")
    # _plt.add(vol.isosurface(isovalue).color(color))
    # _plt.camera = fig2_camera_tilted
    # _plt.show(interactive=False)
    # _plt.screenshot(f"figures/figure-2-panel-{panel}3_tilted.png")
    # _plt.camera = fig2_camera_top
    # _plt.show()
    # _plt.screenshot(f"figures/figure-2-panel-{panel}3_top.png")
    # _plt.camera = fig2_camera_side
    # _plt.show()
    # _plt.screenshot(f"figures/figure-2-panel-{panel}3_side.png")
    # _plt.close()
    # ########

    # Inspection
    txt.text("Check everything is good...")
    plt.show()
    plt.close()

    printc("-> Writing the volume", volume)

    vol.write(volume)

    printc("-> Saving metadata")
    pipeline[channel] = os.path.basename(volume)
    pipeline[f"{channel}_v0"] = v0
    pipeline[f"{channel}_v1"] = v1
    dic2file(pipeline, os.path.join(experiment_folder_path, "pipeline.log"))


def _extract_surface(experiment_folder_path, isovalue, auto):

    # Read the pipeline

    # Make sure the dapi volume exits
    # Get the paths
    pipeline_path = os.path.join(experiment_folder_path, "pipeline.log")
    pipeline = load_pipeline(experiment_folder_path)
    volume = pipeline.get("DAPI", False)

    if not Volume:
        print("Make sure you have clean the DAPI channel volume!")
        return
    volume = os.path.join(experiment_folder_path, volume)
    vol = Volume(volume)

    # If the user selects
    if isovalue:
        iso_value = isovalue
    # If it want it to be automatic
    elif auto:
        printc(
            "We are using automatic isovalue! You can manually pic one by using 20.get_isovalue.py script!"
        )
        h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
        iso_value = h.mean

        iso_value = float(iso_value)

    # Otherwise, allow the user to picl
    else:
        # IsosurfaceBrowser(Plotter) instance:
        plt = IsosurfaceBrowser(vol.color((255, 127, 17, 0)),
                                use_gpu=True,
                                c="green",
                                alpha=0.6)
        plt.show(axes=7, bg2="lb")

        # Get the isosurface value
        iso_value = plt.sliders[0][0].value
        plt.close()
    printc(f"The selected iso value is {iso_value:2f}.", c="orange")

    # Computing isosurface
    printc(f"-> Computing isosurface... iso_value = {iso_value}", c="orange")
    surface = vol.isosurface(iso_value).extract_largest_region()

    # Decimating isosurface
    printc(
        f"-> Decimating isosurface... from n = {surface.npoints} please wait..."
    )
    surface.decimate(0.005)

    path_surface = volume.replace(".vti", "_surface.vtk")
    surface.write(path_surface)
    printc("-> Writing", path_surface)

    # Store the path
    pipeline["SURFACE"] = os.path.basename(path_surface)
    dic2file(pipeline, pipeline_path)


def _stage_limb(experiment_folfer_path):
    # Get the the data from the pipeline file
    pipeline_file = os.path.join(experiment_folfer_path, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    surface = pipeline["SURFACE"]

    # outfile = "/Users/lauavino/Documents/Code/limb-hcr-pipeline/limb-stagig/.tmp_out.txt"

    outfile = os.path.join(experiment_folfer_path, "staging.txt")

    print("Trying to connect to the server...")
    connect = requests.get("http://0.0.0.0:8000")
    if connect.status_code == 200:
        try:
            print(connect.json())
            SERVER = True
        except:
            SERVER = False
            print("Using local exe")

    def kfunc(event):
        if event.keypress == "s":
            if plt.line:
                n = fit_plane(plt.cpoints).normal
                T = LinearTransform().reorient(n, [0, 0, -1], xyplane=True)
                fitpoints = Points(plt.cpoints, c="red5", r=10).pickable(False)
                fitpoints.apply_transform(T).project_on_plane("z").alpha(1)
                fitpoints.name = "Fit"
                fitline = plt.line.clone()
                fitline.apply_transform(T).project_on_plane("z").alpha(1)
                fitline.name = "Fit"
                axes = Axes(fitline, c="k")
                axes.name = "Fit"
                plt.at(1).remove("Fit").add(fitpoints, fitline,
                                            axes).reset_camera()
                #
                # stage the limb
                txt.text("Staging your limb, please wait...")
                plt.render()

                if SERVER:
                    data = {
                        "header":
                        f"gene_mapper tmp.txt  u 1.0  0 0 0 0 {len(fitpoints.coordinates)}\n",
                        "points":
                        list((p[0], p[1])
                             for p in vector(fitpoints.coordinates))
                    }

                    # response = requests.post("http://10.250.4.21:81/stage/", json=data)
                    response = requests.post("http://0.0.0.0:8000/stage/",
                                             json=data,
                                             timeout=1000)
                    print(response)
                    response_data = response.json()
                    print(response_data)
                    stage = response_data['stage']
                else:
                    if os.path.isfile(LIMBSTAGER_EXE):
                        # create an output file to feed the staging system executable

                        with open(outfile, "w", encoding="utf-8") as f:
                            f.write(
                                f"gene_mapper {outfile}  u 1.0  0 0 0 0 {len(fitpoints.coordinates)}\n"
                            )
                            for p in vector(fitpoints.coordinates):
                                f.write(f"MEASURED {p[0]} {p[1]}\n")

                        # now stage: a .tmp_out.txt file is created
                        errnr = os.system(
                            f"{LIMBSTAGER_EXE} {outfile} > {os.path.join(experiment_folfer_path, "staging_fit.txt")} 2> /dev/null"
                        )
                        if errnr:
                            printc(
                                f"limbstager executable {LIMBSTAGER_EXE} returned error:",
                                errnr,
                                c="r",
                            )
                            return
                    else:
                        printc("INFO: limbstager executable not found.",
                               c="lg")
                        return

                    result = grep(os.path.join(experiment_folfer_path, "staging_fit.txt"), "RESULT")
                    if len(result) == 0:
                        printc(
                            "Error - Could not stage the limb, RESULT tag is missing",
                            c="r")
                        return
                    stage = result[0][1]
                txt.text(f"Limb staged as {stage}")
                plt.at(0).render()
                pipeline["STAGE"] = stage

        elif event.keypress == "r":
            plt.reset_camera().render()

        elif event.keypress == "q":
            plt.close()

    settings.use_depth_peeling = True
    settings.enable_default_keyboard_callbacks = False
    settings.default_font = "Dalim"

    # load a 3D mesh of the limb to stage
    surface = os.path.join(experiment_folfer_path, surface)
    msh = Mesh(surface).c("blue8", 0.8)
    txt = Text2D(pos="top-center", bg="yellow5", s=1.5)

    plt = SplinePlotter(msh,
                        title="3D Stager",
                        N=2,
                        sharecam=0,
                        size=(2000, 1000),
                        axes=14)
    plt.verbose = False
    plt.instructions.text(("Click to add a point\n"
                           "Right-click to remove it\n"
                           "Press c to clear points\n"
                           "Press s to stage the limb\n"
                           "Press r to reset camera\n"
                           "Press q to quit"))
    plt.add_callback("on keypress", kfunc)
    plt.at(0).add(Axes(msh, c="k", xygrid=False, ztitle=" "))
    plt.at(1).add(txt)
    plt.at(0).show(interactive=True)
    plt.close()

    dic2file(pipeline, pipeline_file)

    def _rotate_limb():
        return

    def _morph_limb():
        return


def _rotate_limb(experiment_folfer_path):
    pipeline_file = os.path.join(experiment_folfer_path, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    surface = pipeline.get("BLENDER", pipeline["SURFACE"])
    stage = pipeline.get("STAGE", False)

    print(surface, stage)

    # side = pipeline.get("SIDE")

    if not stage:
        print("Please run the staging algorithm first!")
        sys.exit(0)

    # Get the target stage
    reference_stage = closest_value(reference_stages, int(stage))
    print(
        f"The stage of the limb is {stage} and we are using as reference {reference_stage}."
    )
    refence_limb = get_reference_limb(reference_stage)
    print(f"The reference limb is in file {refence_limb}.")

    # Get the Surfaces
    source = Mesh(os.path.join(experiment_folfer_path, surface)).color(
        (252, 171, 16)).scale(1.1)
    target = (
        Mesh(refence_limb).cut_with_plane(origin=(1, 0, 0))
        # .color("yellow5")
        .alpha(0.5).color((43, 158, 179)))

    printc("Manually align mesh by toggling 'a'", invert=True)
    # show(, axes=14).close()

    # Store the Transformation
    T = source.apply_transform_from_actor()
    tname = surface.replace("_surface.vtk", "_rotation.mat")
    # if os.path.isfile(tname):
    #     answer = vedo.ask("Overwrite existing transformation matrix? (y/N)",
    #                       c="y")
    #     if answer == "y":
    #         # T.filename = tname
    #         T.write(os.path.join(experiment_folfer_path, tname))
    #         print(T)
    # else:
    #     print("Saving!")
    #     T.write(os.path.join(experiment_folfer_path, tname))
    #     print(T)

    plt = Plotter(shape="1|2", sharecam=False)

    plt.at(2).camera = dict(
        position=(727.482, -9177.46, 178.073),
        focal_point=(727.482, 387.830, 178.073),
        viewup=(2.82523e-34, -2.37707e-17, 1.00000),
        roll=1.61874e-32,
        distance=9565.29,
        clipping_range=(7962.46, 11606.0),
    )

    plt.at(1).camera = dict(
        position=(727.482, 387.830, 9725.70),
        focal_point=(727.482, 387.830, 178.073),
        viewup=(0, 1.00000, 0),
        roll=0,
        distance=9547.62,
        clipping_range=(8305.31, 11134.5),
    )

    # plt.at(2).freeze()

    plt.at(2).add(source.alpha(0.4), target.alpha(0.6))
    plt.at(1).add(source.alpha(0.4), target.alpha(0.6))
    plt.at(0).add(source.alpha(0.4), target.alpha(0.6))

    # plt.at(2).freeze()

    plt.show(axes=14).interactive()
    plt.close()
    # print(plt.warped.transform)
    T = source.transform
    print(T)
    T.write(os.path.join(experiment_folfer_path, tname))

    pipeline["TRANSFORMATION"] = os.path.basename(tname)
    pipeline["ROTATION"] = os.path.basename(tname)
    dic2file(pipeline, pipeline_file)


def _morph_limb(experiment_folfer_path):
    pipeline_file = os.path.join(experiment_folfer_path, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    surface = os.path.join(experiment_folfer_path, pipeline["SURFACE"])
    stage = pipeline.get("STAGE", False)

    if not stage:
        print("Please run the staging algorithm first!")
        exit()

    settings.default_font = "Calco"
    settings.enable_default_mouse_callbacks = False

    source = Mesh(surface).color("k5")
    # source.rotate_y(90).rotate_z(-60).rotate_x(40)

    # Get the target stage
    reference_stage = closest_value(reference_stages, int(stage))
    print(
        f"The stage of the limb is {stage} and we are using as reference {reference_stage}."
    )
    refence_limb = get_reference_limb(reference_stage)
    print(f"The reference limb is in file {refence_limb}.")
    target = Mesh(refence_limb).color("yellow5", 0.8)

    plt = MorphPlotter(source, target, axes=14)
    plt.show()
    # print(plt.warped.transform)
    wrap_transform = plt.warped.transform
    plt.close()

    tname = surface.replace("_surface.vtk", "_morphing.mat")
    wrap_transform.write(tname)
    print(wrap_transform)

    pipeline["TRANSFORMATION"] = tname
    pipeline["MORPHING"] = tname
    dic2file(pipeline, pipeline_file)
