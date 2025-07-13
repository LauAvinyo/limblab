import os
import sys

import numpy as np
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





def _clean_volume(experiment_folder_path, raw_volume, channel, verbose=True, 
                 gaussian_sigma=None, frequency_cutoff=None, low_res_size=None):
    """
    Clean and preprocess volume data for limb analysis.
    
    This function performs volume cleaning including thresholding, smoothing,
    and filtering operations. It processes the raw volume and saves the cleaned
    version to the experiment folder.
    
    Args:
        experiment_folder_path: Path to the experiment folder containing pipeline.log
        raw_volume: Path to the raw volume file (.tif format)
        channel: Channel name (e.g., 'DAPI', 'GFP', 'RFP') - will be converted to uppercase
        verbose: Whether to print processing information (default: True)
        gaussian_sigma: Tuple of (x, y, z) for gaussian smoothing. Default: (6, 6, 6)
        frequency_cutoff: Frequency cutoff for low-pass filtering. Default: 0.05
        low_res_size: Tuple of (x, y, z) for output volume size. Default: (512, 512, 296)
    
    Returns:
        None. Saves cleaned volume to experiment folder and updates pipeline.log
    
    Example:
        >>> _clean_volume("./experiment", "raw_data.tif", "DAPI")
        >>> _clean_volume("./experiment", "raw_data.tif", "GFP", 
        ...              gaussian_sigma=(8, 8, 8), frequency_cutoff=0.03)
    """

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

    # Use provided parameters or defaults
    SIGMA = gaussian_sigma if gaussian_sigma is not None else (6, 6, 6)
    CUTOFF = frequency_cutoff if frequency_cutoff is not None else 0.05
    SIZE = low_res_size if low_res_size is not None else (512, 512, 296)  # low res
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
    printc("Smothing done! Check bac the plotter!")

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
    """
    Extract surface mesh from volume data using isosurface extraction.
    
    This function creates a 3D surface mesh from the DAPI volume using isosurface
    extraction. The surface is then decimated for optimization and saved as a VTK file.
    
    Args:
        experiment_folder_path: Path to the experiment folder containing pipeline.log
        isovalue: Specific isovalue to use for surface extraction. If None, will be determined interactively or automatically
        auto: If True, automatically determine isovalue from volume histogram. If False, use interactive selection
    
    Returns:
        None. Saves surface mesh to experiment folder and updates pipeline.log
    
    Note:
        Requires a cleaned DAPI volume to exist in the experiment folder.
        The surface will be decimated to 0.5% of original points for performance.
    
    Example:
        >>> _extract_surface("./experiment", isovalue=200, auto=False)
        >>> _extract_surface("./experiment", isovalue=None, auto=True)
    """

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


def _stage_limb(experiment_folder_path, limb_stager=None):
    """
    Stage the limb using 3D spline fitting and automated staging.
    
    This function opens an interactive 3D viewer where you can place points along
    the limb to create a spline. The spline is then used to determine the limb stage
    either via online API or local executable.
    
    Args:
        experiment_folder_path: Path to the experiment folder containing the surface mesh
        limb_stager: Path to local limbstager executable. If None, uses online API
    
    Returns:
        None. Updates pipeline.log with the determined stage
    
    Interactive Controls:
        - Click to add points along the limb
        - Right-click to remove points
        - Press 'c' to clear all points
        - Press 's' to stage the limb
        - Press 'r' to reset camera
        - Press 'q' to quit
    
    Note:
        Requires a surface mesh to exist in the experiment folder.
        The staging uses a spline fit to the placed points to determine limb stage.
    
    Example:
        >>> _stage_limb("./experiment")
        >>> _stage_limb("./experiment", limb_stager="/path/to/limbstager")
    """
    # Get the the data from the pipeline file
    pipeline_file = os.path.join(experiment_folder_path, "pipeline.log")
    pipeline = file2dic(pipeline_file)
    surface = pipeline["SURFACE"]

    if limb_stager is not None:
        LIMBSTAGER_EXE = limb_stager
    else:
        LIMBSTAGER_EXE = None

    outfile = os.path.join(experiment_folder_path, "staging.txt")

    STAGING_URL = "https://limbstaging.embl.es/api"
    connect = requests.get(STAGING_URL)
    if connect.status_code == 200:
        try:
            response = connect.json()
            print(response)
            SERVER = True
        except:
            SERVER = False
            print("We could not connect to the staging system. Please try again, use local exe or contact us.")

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

                    response = requests.post(f"{STAGING_URL}/stage/",
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
                            f"{LIMBSTAGER_EXE} {outfile} > {os.path.join(experiment_folder_path, 'staging_fit.txt')} 2> /dev/null"
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

                    result = grep(
                        os.path.join(experiment_folder_path,
                                     'staging_fit.txt'), "RESULT")
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


def _rotate_limb(experiment_folder_path):
    """
    Rotate and align the limb using interactive 3D transformation.
    
    This function opens an interactive 3D viewer where you can manually align
    the limb with a reference limb of the same stage. The transformation is
    saved and can be applied to other data.
    
    Args:
        experiment_folder_path: Path to the experiment folder containing the surface mesh
    
    Returns:
        None. Saves transformation matrix to experiment folder and updates pipeline.log
    
    Interactive Controls:
        - Use mouse to rotate, pan, and zoom
        - Toggle 'a' to apply transformation
        - The transformation is automatically saved when you close the viewer
    
    Note:
        Requires a surface mesh and stage information to exist in the experiment folder.
        The reference limb is automatically selected based on the determined stage.
    
    Example:
        >>> _rotate_limb("./experiment")
    """
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
    """
    Morph the limb to match a reference template using non-linear registration.
    
    This function performs non-linear morphing of the limb surface to align
    it with a reference template of the same stage. The morphing transformation
    is saved and can be applied to other data.
    
    Args:
        experiment_folder_path: Path to the experiment folder containing the surface mesh
    
    Returns:
        None. Saves morphed surface and transformation to experiment folder
    
    Note:
        Requires a surface mesh, stage information, and rotation transformation
        to exist in the experiment folder. The reference template is automatically
        selected based on the determined stage.
    
    Example:
        >>> _morph_limb("./experiment")
    """
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
