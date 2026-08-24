from pathlib import Path
from limblab import params
from vedo import Volume, Plotter, Text2D
from vedo.applications import IsosurfaceBrowser

from limblab.models import Channel, Experiment
from limblab.params import CleanParams
from limblab.exceptions import VolumeProcessingError
from limblab.utils import generate_kwargs

from typing import Optional, Any, Literal

from limblab.design import theme


def pick_isovalues(
    raw_volume_path: Path,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
    ) -> tuple[int, int] | Any:
    vol = Volume(str(raw_volume_path))

    ''''
    Opens the vedo IsosurfaceBrowser and lets the user pick lower/upper
    isovalues interactively. Returns (v0, v1).
    '''

    vol = Volume(str(raw_volume_path))


    params: dict[str, Any] = dict(use_gpu=True, bg = theme("palette.background"), c=theme("limblab.surface"), alpha=0.6)
    kwargs = generate_kwargs(
        params=params, renderer=renderer, outside_class=outside_class
    )

    plt = IsosurfaceBrowser(vol, **kwargs)

    if renderer == "pyqt":
        plt.show(interactive=False)
        return plt  # caller reads plt.sliders[0][0].value on demand

    # Standalone behaviour (unchanged)
    #no need to add sliders in the vedo plotter! these are selected through UI
    txt = Text2D(pos="top-center", bg="yellow5", s=1.5)
    plt += txt

    txt.text("Select the lower isovalue, then press 'q' to confirm")
    plt.show().interactive()
    v0 = int(plt.sliders[0][0].value)

    txt.text("Select the upper isovalue, then press 'q' to confirm")
    plt.show().interactive()
    v1 = int(plt.sliders[0][0].value)

    plt.close()

    if v0 == v1:
        v1 += 1

    return v0, v1


def get_channel_path(experiment: Experiment, channel_name: str) -> Path:
    channel_name = channel_name.lower()
    for channel in experiment.channels:
        if channel.channel_name.lower() == channel_name:
            return Path(experiment.base) / channel.path
    raise VolumeProcessingError(f"No '{channel_name}' channel found on experiment.")


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
    vol.threshold(below=params.v0, replace=0).threshold(
        above=params.v1, replace=params.v1
    )
    vol.resize([params.low_res_size] * 3)

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
        clean_isovalue_min=params.v0,
        clean_isovalue_max=params.v1,
    )
