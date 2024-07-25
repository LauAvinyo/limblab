# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from enum import Enum
from pathlib import Path
from typing import List

import typer
from typing_extensions import Annotated
from visualitzations import (one_channel_isosurface, probe, raycast, slices,
                             two_chanel_isosurface)

app = typer.Typer()

# TODO: Think if we really want to use this or change the name of the argument.
EXPERIMENT_FOLDER_HELP = "Path to the experiment folder"


class VisAlgorithm(str, Enum):
    isosurfces = "isosurfaces"
    raycast = "raycast"
    # slab = "slab"
    slices = "slices"
    probe = "probe"


@app.command()
def create_experiment(experiment_name: str, experiment_folder_path: Path):
    print(
        f"This will create the experiment folder {experiment_name} on path {experiment_folder_path}"
    )


@app.command()
def clean_volume(experiment_folder_path: Path, volume_path: str):
    print(experiment_folder_path, volume_path)


@app.command()
def extract_surface(
    experiment_folder_path: Annotated[
        Path, typer.Argument(help="Path to the experiment folder")],
    auto: Annotated[
        bool,
        typer.Option(
            help="Automatically pick the isovalue for the surface")] = False):
    print(experiment_folder_path, auto)


@app.command()
def stage(experiment_folder_path: Annotated[Path,
                                            typer.Argument(
                                                help=EXPERIMENT_FOLDER_HELP)]):
    print(experiment_folder_path)


@app.command()
def align(
    experiment_folder_path: Annotated[
        str, typer.Argument(help="Path to the experiment folder")],
    morphing: Annotated[
        bool,
        typer.Option(
            help="Automatically pick the isovalue for the surface")] = False):
    print(experiment_folder_path, morphing)


@app.command()
def visualize(algorithm: VisAlgorithm, experiment_folder_path: Path,
              channels: List[str]):
    print(algorithm, channels)
    if algorithm == VisAlgorithm.isosurfces:
        if len(channels) == 2:
            two_chanel_isosurface(experiment_folder_path, *channels)
        elif len(channels) == 1:
            one_channel_isosurface(experiment_folder_path, channels[0])
        else:
            raise NotImplementedError
    if algorithm == VisAlgorithm.raycast:
        if len(channels) > 1:
            print(
                f"WARNING: Raycast only uses one channel. Using {channels[0]}")
        raycast(experiment_folder_path, channels[0])

    if algorithm == VisAlgorithm.slices:
        slices(experiment_folder_path, channels[0])

    if algorithm == VisAlgorithm.probe:
        probe(experiment_folder_path, channels[0])


if __name__ == "__main__":
    app()
