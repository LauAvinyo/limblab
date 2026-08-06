
from typing import Optional, Any, Literal

def generate_kwargs(params: dict[str, Any], renderer: Optional[Literal["pyqt"]] = None, outside_class: Optional[Any] = None) -> dict[str, Any]:
    # TODO: maybe i can like split this function into smaller pieces.
    kwargs: dict[str, Any] = params

    if renderer == "pyqt":
        if outside_class is None:
            raise ValueError("outside_class must be provided when renderer is 'pyqt'")
        kwargs["qt_widget"] = outside_class.vtkWidget

    return kwargs


styles = {
    0: ("#9ce4f3", "#128099"),
    1: ("#ec96f2", "#c90dd6"),
    "positions": {
        "number": ([0.1, 0.25], [0.2, 0.25]),
        "values": ([0.1, 0.1], [0.2, 0.1])
    },
    "channel_0": {
        "color": "#B0DB43"
    },
    "channel_1": {
        "color": "#db43b0"
    },
    "channel_2": {
        "color": "#43b0db"
    },
    "limb": {
        "alpha": 0.1,
        "color": "#FF7F11"
    },
    "reference": {
        "alpha": 1,
        "color": 1
    },
    "isosurfaces": {
        "alpha": 0.3,
        "alpha-unique": 0.8
    },
    "ui": {
        "primary": "#0d1b2a",
        "secondary": "#fb8f00"
    }
}