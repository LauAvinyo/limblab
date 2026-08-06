
from typing import Optional, Any, Literal
import os

def generate_kwargs(params: dict[str, Any], renderer: Optional[Literal["pyqt"]] = None, outside_class: Optional[Any] = None) -> dict[str, Any]:
    # TODO: maybe i can like split this function into smaller pieces.
    kwargs: dict[str, Any] = params

    if renderer == "pyqt":
        if outside_class is None:
            raise ValueError("outside_class must be provided when renderer is 'pyqt'")
        kwargs["qt_widget"] = outside_class.vtkWidget

    return kwargs