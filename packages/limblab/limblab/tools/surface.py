# limblab/tools/surface.py
from pathlib import Path
from typing import Any, Literal, Optional
from vedo import Volume
from vedo.pyplot import histogram
from vedo.applications import IsosurfaceBrowser

from limblab.models import Experiment, Channel
from limblab.exceptions import VolumeProcessingError
from limblab.utils import generate_kwargs
import os


CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
REFERENCE_LIMB_FOLDER = os.path.join(os.path.dirname(CURRENT_DIR), "limb")
REFERENCE_LIMB_FOLDER = "C:\\Users\\millan\\Desktop\\limblab\\packages\\limblab\\limblab\\limb"
# TODO: FIX THIS!

files = [
    file
    for file in os.listdir(REFERENCE_LIMB_FOLDER)
    if os.path.isfile(os.path.join(REFERENCE_LIMB_FOLDER, file))
    and not file.startswith(".DS")
    or file.startswith("-")
]
reference_stages = [int(file.split(".")[0].split("_")[1]) for file in files]
# DE-COMMENT -> i don't have the files yet!


def auto_isovalue(raw_volume_path: Path) -> float:
    """Automatically determine isovalue from volume histogram."""
    vol = Volume(str(raw_volume_path))
    h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
    return float(h.mean)  # type: ignore

#pick isovalue is the interactive function of the surface action, as it takes the renderer and the outside class
#its also responsible for returning the plotter, source and surface path for writting
def pick_isovalue(
    raw_volume_path: Path,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> float | Any:
    vol = Volume(str(raw_volume_path))


    params: dict[str, Any] = dict(use_gpu=True, c="green", alpha=0.6)
    kwargs = generate_kwargs(
        params=params, renderer=renderer, outside_class=outside_class
    )

    plt = IsosurfaceBrowser(vol.color((255, 127, 17, 0)), **kwargs)

    #allows to extracte the selected isovalue through the vedo slider
    if renderer == "pyqt":
        plt.show(axes=7, bg2="lb", interactive=False)
        return plt

    plt.show(axes=7, bg2="lb").interactive()
    iso_value = plt.sliders[0][0].value
    plt.close()
    return float(iso_value)


#helper function for extract surface to not use the loop for detecting dapi files and perform teh extraction
def get_nuclei_channel_path(experiment: Experiment) -> Path:
    for channel in experiment.channels:
        if channel.channel_name.lower() in ("dapi", "nuclei"):
            result = Path(experiment.base) / channel.path
            
            return result
    raise VolumeProcessingError("No DAPI/nuclei channel found on experiment.")


def extract_surface(
    experiment: Experiment,
    isovalue: float,
    decimate_fraction: float = 0.005,
) -> Path:
    """
    Deterministic surface extraction given an explicit isovalue.
    No interactivity, no histogram/auto logic — caller decides isovalue.

    Returns the path to the saved surface mesh.
    """

    nuclei_channel_path = get_nuclei_channel_path(experiment=experiment)

    vol = Volume(str(nuclei_channel_path))
    surface = vol.isosurface(isovalue).extract_largest_region()
    surface.decimate(decimate_fraction)

    out_path = nuclei_channel_path.with_name(nuclei_channel_path.stem + "_surface.vtk")
    #the selected volume gets outputed as a .vtk volume!

    try:
        surface.write(str(out_path))
    except Exception as e:
        raise VolumeProcessingError(f"Failed to write surface mesh: {e}") from e

    return out_path


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


def _initialize_limbs_paths(experiment: Experiment, reference_stages):
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