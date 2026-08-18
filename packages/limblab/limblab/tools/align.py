import os
import sqlite3
from typing import Any, Literal, Optional

from vedo import Mesh, Plotter, Text2D, settings

from limblab.design import theme
from limblab.models import Experiment
from limblab.utils import generate_kwargs


def _store_transformation_matrix(T, surface_path: str) -> str:
    try:
        transformation_path = surface_path.replace("_surface.vtk", "_rotation.mat")
        T.write(transformation_path)
    except Exception as e:
        raise RuntimeError(f"Failed to write transformation matrix: {e}") from e

    return transformation_path


# ----------------------------------------------------------------------
# DB-backed reference limb lookup
#
# Replaces the old REFERENCE_LIMB_FOLDER filesystem scan (os.listdir +
# filename parsing like "Limb-rec_23.vtk" -> stage 23). 
# ----------------------------------------------------------------------

def _get_reference_stages(db_path: str) -> list[int]:
    """All stages that have a reference limb available in the DB."""
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT stage FROM reference_limbs").fetchall()
    return [row[0] for row in rows]


def _get_reference_limb_path(db_path: str, stage: int) -> Optional[str]:
    """File path for the reference limb at an exact stage, or None."""
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT file_path FROM reference_limbs WHERE stage = ?", (stage,)
        ).fetchone()
    if row is None:
        return None
    file_path = row[0]
    return file_path if os.path.isfile(file_path) else None


def closest_value(input_list: list, target: int) -> int:
    """Get the closest value in the list to our target."""
    closest = input_list[0]
    min_diff = abs(target - closest)

    for value in input_list:
        diff = abs(target - value)
        if diff < min_diff:
            min_diff = diff
            closest = value

    return closest


def _initialize_limbs_paths(experiment: Experiment, db_path: str) -> tuple[str, str]:
    base = experiment.base
    surface_name = experiment.surface_path
    stage = experiment.stage

    if surface_name is None or stage is None or base is None:
        raise ValueError("Experiment must have base, surface, and stage defined.")

    surface_path = os.path.join(base, surface_name)

    reference_stages = _get_reference_stages(db_path)
    if not reference_stages:
        raise RuntimeError("No reference limbs found in the database.")

    reference_stage = closest_value(reference_stages, stage)
    reference_limb_path = _get_reference_limb_path(db_path, reference_stage)

    if reference_limb_path is None:
        raise FileNotFoundError(
            f"No reference limb file found for stage {reference_stage} "
            "(DB row missing, or the file it points to no longer exists on disk)."
        )

    return surface_path, reference_limb_path


def _rotate_limb(
    surface_path: str,
    reference_limb_path: str,
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
) -> str | tuple[Any, Any, str]:

    # Get the Surfaces
    source = Mesh(surface_path).color(theme("limblab.limb", "#000000"))
    target = (
        Mesh(reference_limb_path)
        .cut_with_plane(origin=(1, 0, 0))
        .alpha(0.5)
        .c(theme("limblab.channel0", "#000000"))
    )

    # Store the Transformation
    T = source.apply_transform_from_actor()  # type: ignore

    params: dict[str, Any] = dict(shape="1|2", sharecam=False)
    kwargs = generate_kwargs(params=params, renderer=renderer, outside_class=outside_class)

    plt = Plotter(**kwargs)  # type: ignore

    plt.at(2).camera = {
        "position": (727.482, -9177.46, 178.073),
        "focal_point": (727.482, 387.830, 178.073),
        "viewup": (2.82523e-34, -2.37707e-17, 1.00000),
        "roll": 1.61874e-32,
        "distance": 9565.29,
        "clipping_range": (7962.46, 11606.0),
    }

    plt.at(1).camera = {
        "position": (727.482, 387.830, 9725.70),
        "focal_point": (727.482, 387.830, 178.073),
        "viewup": (0, 1.00000, 0),
        "roll": 0,
        "distance": 9547.62,
        "clipping_range": (8305.31, 11134.5),
    }

    plt.at(2).add(source.alpha(0.4), target.alpha(0.6))  # type: ignore
    plt.at(1).add(source.alpha(0.4), target.alpha(0.6))  # type: ignore
    plt.at(0).add(source.alpha(0.4), target.alpha(0.6))  # type: ignore

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

    if renderer == "pyqt":
        plt.show(axes=14, interactive=False)
        return plt, source, surface_path

    plt += instructions
    plt.show(axes=14).interactive()
    plt.close()

    T = source.transform  # type: ignore

    return _store_transformation_matrix(T, surface_path)


def rotate_limb(
    experiment: Experiment,
    db_path: str,
    renderer: Literal["pyqt"] | None = None,
    outside_class: Any | None = None,
) -> str | tuple[Any, Any, str]:
    """Rotate the limb to a standard orientation, using a reference limb
    looked up from the database rather than a hardcoded folder."""
    settings.enable_default_keyboard_callbacks = True

    surface_path, reference_limb_path = _initialize_limbs_paths(experiment, db_path)

    return _rotate_limb(surface_path, reference_limb_path, renderer, outside_class)


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
