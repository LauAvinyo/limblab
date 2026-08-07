from typing import Optional, Any, Literal
import os

from limblab.models import Experiment
from limblab.utils import generate_kwargs

from colorama import Fore as c
import requests

from vedo import settings
from vedo import vector, Points, LinearTransform, fit_plane
from vedo.applications import SplinePlotter
from vedo import Mesh, Axes, Text2D

MESSAGE = "Could not connect to the staging system. Try again, if the problem persists, contact support."
STAGING_URL = "https://limbstaging.embl.es/api"


def _stage_limb(
    surface: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> int:

    msh = Mesh(surface).c(1).alpha(0.8)  # type: ignore
    txt = Text2D(pos="top-center", bg="yellow5", s=1.5)

    result: dict[str, Any] = {"stage": None}  # container to hold the staged value

    def kfunc(event):
        if event.keypress == "s":
            if plt.line:
                n = fit_plane(plt.cpoints).normal  # type: ignore
                T = LinearTransform().reorient(n, [0, 0, -1], xyplane=True)
                fitpoints = Points(plt.cpoints, c="red5", r=10).pickable(False)
                fitpoints.apply_transform(T).project_on_plane("z").alpha(1)
                fitpoints.name = "Fit"
                fitline = plt.line.clone()
                fitline.apply_transform(T).project_on_plane("z").alpha(1)
                fitline.name = "Fit"
                axes = Axes(fitline, c="k")
                assert axes is not None
                axes.name = "Fit"
                plt.at(1).remove("Fit").add(fitpoints, fitline, axes).reset_camera()
                #
                # stage the limb
                txt.text("Staging limb - please wait...")
                plt.render()

                data = {
                    "header": f"gene_mapper tmp.txt  u 1.0  0 0 0 0 {len(fitpoints.coordinates)}\n",
                    "points": list((p[0], p[1]) for p in vector(fitpoints.coordinates)),
                }

                response = requests.post(
                    f"{STAGING_URL}/stage/", json=data, timeout=1000
                )

                # TODO: handle errors from the staging server
                if response.status_code != 200:
                    raise ConnectionError(
                        f"Staging server returned status code {response.status_code}."
                    )
                response_data = response.json()
                stage = response_data["stage"]
                result["stage"] = stage

                txt.text(f"Limb staged as {stage}")
                plt.at(0).render()

        elif event.keypress == "r":
            plt.reset_camera().render()

        elif event.keypress == "q":
            plt.close()

    params: dict[str, Any] = dict(
        title="3D Stager", N=2, sharecam=0, size=(2000, 1000), axes=14
    )
    kwargs = generate_kwargs(
        params=params, renderer=renderer, outside_class=outside_class
    )

    plt = SplinePlotter(msh, **kwargs)
    plt.verbose = False
    plt.instructions.text(
        (
            "Click to add a point\n"
            "Right-click to remove it\n"
            "Press 'c' to clear all points\n"
            "Press 's' to stage the limb\n"
            "Press 'r' to reset camera\n"
            "Press 'q' to quit"
        )
    )
    plt.add_callback("on keypress", kfunc)
    plt.at(0).add(Axes(msh, c="k", xygrid=False, ztitle=" "))
    plt.at(1).add(txt)
    plt.at(0).show(interactive=True)
    plt.close()

    return result["stage"]


def check_connection(url: str) -> None:
    # Test the Limbstaging Server
    connect = requests.get(STAGING_URL)
    if connect.status_code == 200:
        try:
            response = connect.json()
            print(c.GREEN + str(response["message"]) + c.RESET)
        except:
            raise ConnectionError(MESSAGE)
    else:
        raise ConnectionError(MESSAGE)


def stage_limb(experiment: Experiment) -> int:
    """ """
    # Vedo settings
    settings.use_depth_peeling = True
    settings.enable_default_keyboard_callbacks = False

    check_connection(STAGING_URL)

    surface_name = experiment.surface
    base = experiment.base
    if surface_name is None or base is None:
        raise ValueError(
            "Surface name and base path must be provided in the experiment object."
        )

    surface = os.path.join(base, surface_name)

    stage = _stage_limb(surface)

    return stage
