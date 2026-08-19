from pathlib import Path
from vedo import Volume, Plotter

from limblab.utils import generate_kwargs

from typing import Optional, Any, Literal
from limblab.design import theme


def preview_volume(
    raw_volume_path: Path,
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> Any:
    """
    Opens a plain, non-interactive-picking view of a raw volume.
    No isovalue sliders, no clean parameters — just a first look.
    """
    vol = Volume(str(raw_volume_path))
    spacing = (0.65,0.65,2)

    vol.spacing(spacing)

    vol.resize([524 // 2] * 3)

    params: dict[str, Any] = dict(bg = theme("palett.background"))
    kwargs = generate_kwargs(
        params=params, renderer=renderer, outside_class=outside_class
    )

    plt = Plotter(**kwargs)
    plt += vol

    if renderer == "pyqt":
        plt.show(interactive=False)
        return plt  # caller owns the render loop via the embedding widget

    plt.show(interactive=True)
    plt.close()
    return plt