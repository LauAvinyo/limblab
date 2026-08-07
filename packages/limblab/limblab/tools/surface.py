# limblab/tools/surface.py
from pathlib import Path
from typing import Any, Literal, Optional
from vedo import Volume
from vedo.pyplot import histogram
from vedo.applications import IsosurfaceBrowser

from limblab.models import Experiment, Channel
from limblab.exceptions import VolumeProcessingError
from limblab.utils import generate_kwargs


def auto_isovalue(raw_volume_path: Path) -> float:
    """Automatically determine isovalue from volume histogram."""
    vol = Volume(str(raw_volume_path))
    h = histogram(vol, bins=75, logscale=1, max_entries=1e5)
    return float(h.mean)  # type: ignore


def pick_isovalue(
    raw_volume_path: Path,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> float:
    """Opens the vedo IsosurfaceBrowser and lets the user pick a single isovalue."""
    vol = Volume(str(raw_volume_path))

    params: dict[str, Any] = dict(use_gpu=True, c="green", alpha=0.6)
    kwargs = generate_kwargs(
        params=params, renderer=renderer, outside_class=outside_class
    )

    plt = IsosurfaceBrowser(vol.color((255, 127, 17, 0)), **kwargs)
    plt.show(axes=7, bg2="lb")
    iso_value = plt.sliders[0][0].value
    plt.close()
    return float(iso_value)


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
    for channel in experiment.channels:
        if channel.channel_name.lower() == "nuclei":
            nuclei_channel_path = Path(channel.path)
            break

    vol = Volume(str(nuclei_channel_path))
    surface = vol.isosurface(isovalue).extract_largest_region()
    surface.decimate(decimate_fraction)

    out_path = nuclei_channel_path.with_name(nuclei_channel_path.stem + "_surface.vtk")
    try:
        surface.write(str(out_path))
    except Exception as e:
        raise VolumeProcessingError(f"Failed to write surface mesh: {e}") from e

    return out_path
