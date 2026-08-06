from typing import Optional, Any, Literal
import os

from limblab.models import Experiment
from limblab.tools import stage
from limblab.utils  import generate_kwargs  
from colorama import Fore as c

from vedo import settings
from vedo import Plotter, Mesh, Axes, Text2D
from vedo.applications import IsosurfaceBrowser, MorphPlotter, SplinePlotter
from vedo import Mesh, Axes, Text2D


CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
REFERENCE_LIMB_FOLDER = os.path.join(os.path.dirname(CURRENT_DIR), "limb")
REFERENCE_LIMB_FOLDER = "/Users/laura/limblab/packages/limblab/limblab/limb"
# TODO: FIX THIS!

files = [
    file
    for file in os.listdir(REFERENCE_LIMB_FOLDER)
    if os.path.isfile(os.path.join(REFERENCE_LIMB_FOLDER, file))
    and not file.startswith(".DS")
    or file.startswith("-")
]

reference_stages = [int(file.split(".")[0].split("_")[1]) for file in files]


def closest_value(input_list: list, target: int) -> int:
    """ "Get the closest value of the list to our target."""
    closest = input_list[0]  # Assume the first value is the closest initially
    min_diff = abs(target - closest)  # Initialize minimum difference

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest



def get_reference_limb(stage: int) -> str | None:
    """From the stage, get the reference limb path"""
    file = os.path.join(REFERENCE_LIMB_FOLDER, "Limb-rec_" + str(stage) + ".vtk")
    if os.path.isfile(file):
        return file
    return None

def _store_transformation_matrix(T, surface_path: str) -> str:

    try:
        transformation_path = surface_path.replace("_surface.vtk", "_rotation.mat")
        T.write(transformation_path)
    except Exception as e:
        raise RuntimeError(f"Failed to write transformation matrix: {e}") from e

    return transformation_path


def _initialize_limbs_paths(experiment: Experiment,):
    base = experiment.base
    surface_name = experiment.surface
    stage = experiment.stage

    if surface_name is None or stage is None or base is None:
        raise ValueError("Experiment must have base, surface, and stage defined.")

    surface_path = os.path.join(base, surface_name)

    # Get the target stage
    reference_stage = closest_value(reference_stages, stage)
    refence_limb_path = get_reference_limb(reference_stage)

    if refence_limb_path is None:
        raise FileNotFoundError(f"No reference limb found for stage {reference_stage}")


    return surface_path, refence_limb_path

def _rotate_limb(
    surface_path: str,
    reference_limb_path: str,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> str:

    # Get the Surfaces
    source = Mesh(surface_path).color(1)  # .scale(1.1)
    target = Mesh(reference_limb_path).cut_with_plane(origin=(1, 0, 0)).alpha(0.5).c(2)

    # Store the Transformation
    T = source.apply_transform_from_actor() # type: ignore

    params: dict[str, Any] = dict(shape="1|2", sharecam=False)
    kwargs = generate_kwargs(params=params, renderer=renderer, outside_class=outside_class)

    plt = Plotter(**kwargs) # type: ignore

    # Set the camera positions for the three views
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

    plt.at(2).add(source.alpha(0.4), target.alpha(0.6))
    plt.at(1).add(source.alpha(0.4), target.alpha(0.6))
    plt.at(0).add(source.alpha(0.4), target.alpha(0.6))

    plt.verbose = False # type: ignore

    # Add instructions as Text2D instead of using plt.instructions.text()
    instructions = Text2D(
        "Toggle 'a' for transformation mode\n"
        "Use mouse to rotate\n"
        "+ctrl to fix rotation axis\n"
        "+shift to translate\n"
        "right click to scale",
        pos="top-center",
        bg="green5",
        s=1.2,
    )

    # Add instructions to the main plotter
    plt += instructions

    plt.show(axes=14).interactive()
    plt.close()
    
    T = source.transform # type: ignore

    return _store_transformation_matrix(T, surface_path)


def rotate_limb(
    experiment: Experiment,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> str:
    """
    Rotate the limb to a standard orientation.
    This function is a placeholder and should be implemented with the actual rotation logic.
    """

    surface_path, refence_limb_path = _initialize_limbs_paths(experiment)

    return _rotate_limb(surface_path, refence_limb_path, renderer, outside_class)


# def _morph_limb(
#     surface_path: str,
#     reference_limb_path: str,
#     renderer: Optional[Literal["pyqt"]] = None,
#     outside_class: Optional[Any] = None,
# ) -> str:
#     """
#     Morph the limb to a standard orientation.
#     This function is a placeholder and should be implemented with the actual morphing logic.
#     """


#     settings.enable_default_mouse_callbacks = False

#     source = Mesh(surface_path).color("k5")
#     target = Mesh(reference_limb_path).color("yellow5", 0.8)

#     params: dict[str, Any] = dict(axes=14)
#     kwargs = generate_kwargs(params=params, renderer=renderer, outside_class=outside_class)

#     plt = MorphPlotter(source, target)
#     plt.show()
#     wrap_transform = plt.warped.transform
#     plt.close()

#     return _store_transformation_matrix(wrap_transform, surface_path)



# def morph_limb(experiment: Experiment, renderer: Optional[Literal["pyqt"]] = None, outside_class: Optional[Any] = None) -> str:
#     """
#     Morph the limb to a standard orientation.
#     This function is a placeholder and should be implemented with the actual morphing logic.
#     """

#     surface_path, refence_limb_path = _initialize_limbs_paths(experiment)

#     return _morph_limb(surface_path, refence_limb_path, renderer, outside_class)