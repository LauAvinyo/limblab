from tools import _stage_limb
import requests
import certifi
import vedo
import os
from vedo import (Axes, LinearTransform, Mesh, Plotter, Points, Text2D, Volume,
                  fit_plane, grep, printc, settings, vector)
from vedo.applications import IsosurfaceBrowser, MorphPlotter, SplinePlotter
outfile = "staging.txt"

STAGING_URL = "https://limbstaging.embl.es/api"
print("Trying to connect to the server...")
connect = requests.get(STAGING_URL, verify=certifi.where())
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

                response = requests.post(f"{STAGING_URL}/stage/",
                                            json=data,
                                            timeout=1000)
                print(response)
                response_data = response.json()
                print(response_data)
                stage = response_data['stage']
            txt.text(f"Limb staged as {stage}")
            plt.at(0).render()
            print(f"The stage is {stage}")

    elif event.keypress == "r":
        plt.reset_camera().render()

    elif event.keypress == "q":
        plt.close()

settings.use_depth_peeling = True
settings.enable_default_keyboard_callbacks = False
settings.default_font = "Dalim"

# load a 3D mesh of the limb to stage
surface = os.path.join("limb", "Limb-rec_265.vtk")
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



