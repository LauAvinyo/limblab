from typing import Any, Literal, Optional

from limblab.design import theme


def generate_kwargs(
    params: dict[str, Any],
    renderer: Optional[Literal["pyqt"]] = None,
    outside_class: Optional[Any] = None,
) -> dict[str, Any]:
    # TODO: maybe i can like split this function into smaller pieces.
    kwargs: dict[str, Any] = params

    if renderer == "pyqt":
        if outside_class is None:
            raise ValueError("outside_class must be provided when renderer is 'pyqt'")
        kwargs["qt_widget"] = outside_class.vtk_widget

    return kwargs


def _get_palette_color(key: str, default: str) -> str:
    try:
        return theme(f"palette.{key}", default)
    except Exception:
        return default

styles = {
    0: (_get_palette_color("channel0", "#9ce4f3"), _get_palette_color("channel1", "#128099")),
    1: (_get_palette_color("channel1", "#ec96f2"), _get_palette_color("channel2", "#c90dd6")),
    "positions": {
        "number": ([0.1, 0.25], [0.2, 0.25]),
        "values": ([0.1, 0.1], [0.2, 0.1]),
    },
    "channel_0": {"color": _get_palette_color("channel0", "#B0DB43")},
    "channel_1": {"color": _get_palette_color("channel1", "#db43b0")},
    "channel_2": {"color": _get_palette_color("channel2", "#43b0db")},
    "limb": {"alpha": 0.1, "color": _get_palette_color("limb", "#FF7F11")},
    "reference": {"alpha": 1, "color": _get_palette_color("reference", 1)},
    "isosurfaces": {"alpha": 0.3, "alpha-unique": 0.8},
    "ui": {"primary": _get_palette_color("primary", "#0d1b2a"), "secondary": _get_palette_color("secondary", "#fb8f00")},
}
