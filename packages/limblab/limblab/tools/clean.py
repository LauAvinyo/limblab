from pathlib import Path
from vedo import Volume, Plotter, Text2D
from vedo.applications import IsosurfaceBrowser

from limblab.models import Channel, Experiment
from limblab.params import CleanParams
from limblab.exceptions import VolumeProcessingError

from typing import Optional, Any, Literal



def pick_isovalues(raw_volume_path: Path, renderer: Optional[Literal["pyqt"]] = None, outside_class: Optional[Any] = None) -> tuple[int, int]:
    """
    Opens the vedo IsosurfaceBrowser and lets the user pick lower/upper
    isovalues interactively. Returns (v0, v1).
    """
    vol = Volume(str(raw_volume_path))

    kwargs: dict[str, Any] = dict(use_gpu=True, bg="white", c="green", alpha=0.6)
    if renderer == "pyqt":
        if outside_class is None:
            raise ValueError("outside_class must be provided when renderer is 'pyqt'")
        kwargs["qt_widget"] = outside_class.vtkWidget


    plt = IsosurfaceBrowser(vol, **kwargs) 
    txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
    plt += txt

    txt.text("Select the lower isovalue, then press 'q' to confirm")
    plt.show()
    v0 = int(plt.sliders[0][0].value)

    txt.text("Select the upper isovalue, then press 'q' to confirm")
    plt.show()
    v1 = int(plt.sliders[0][0].value)

    plt.close()

    if v0 == v1:
        v1 += 1

    return v0, v1


def clean(
    experiment: Experiment,
    raw_volume_path: Path,
    channel_name: str,
    params: CleanParams,
) -> Channel:
    """Deterministic clean given explicit params. No interactivity."""
    channel_name = channel_name.upper()
    spacing = (experiment.spacing_x, experiment.spacing_y, experiment.spacing_z)

    vol = Volume(str(raw_volume_path))
    vol.spacing(spacing)
    vol = vol.cmap("Purples", vmin=params.v0, vmax=params.v1)
    vol.threshold(below=params.v0, replace=0).threshold(above=params.v1, replace=params.v1)
    vol.resize(params.low_res_size)

    if experiment.side == "L":
        vol.mirror()

    vol.smooth_gaussian(sigma=params.gaussian_sigma)
    vol.frequency_pass_filter(high_cutoff=params.frequency_cutoff)

    out_path = raw_volume_path.with_suffix(".vti")
    try:
        vol.write(str(out_path))
    except Exception as e:
        raise VolumeProcessingError(f"Failed to write cleaned volume: {e}") from e

    return Channel(
        experiment_id=experiment.experiment_id,
        channel_name=channel_name,
        path=str(out_path),
        v0=params.v0,
        v1=params.v1,
    )