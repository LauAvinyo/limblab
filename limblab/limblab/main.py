# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error

import os
import shutil
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from limblab.pipeline import _create_experiment
from limblab.tools import (_clean_volume, _extract_surface, _morph_limb,
                           _rotate_limb, _stage_limb)
from limblab.visualitzations import (dynamic_slab, one_channel_isosurface,
                                     probe, raycast, slices,
                                     two_chanel_isosurface)

app = typer.Typer()

# TODO: Think if we really want to use this or change the name of the argument.
EXPERIMENT_FOLDER_HELP = "Path to the experiment folder"


class VisAlgorithm(str, Enum):
    isosurfces = "isosurfaces"
    raycast = "raycast"
    slab = "slab"
    slices = "slices"
    probe = "probe"


@app.command()
def create_experiment(
        experiment_name: str,
        experiment_folder_path: Annotated[Optional[str],
                                          typer.Argument()] = None):
    if experiment_folder_path is None:
        experiment_folder_path = "./"
    _create_experiment(experiment_folder_path, experiment_name)
    print(
        f"This will create the experiment folder {experiment_name} on path {experiment_folder_path}"
    )


@app.command()
def clean_volume(experiment_folder_path: Path, volume_path: Path,
                 channel_name: str):
    _clean_volume(experiment_folder_path, volume_path, channel_name)


@app.command()
def extract_surface(
    experiment_folder_path: Annotated[
        Path, typer.Argument(help="Path to the experiment folder")],
    isovalue: Annotated[Optional[int], typer.Argument()] = None,
    auto: Annotated[
        bool,
        typer.Option(
            help="Automatically pick the isovalue for the surface")] = False):
    _extract_surface(experiment_folder_path, isovalue, auto)


@app.command()
def stage(experiment_folder_path: Annotated[Path,
                                            typer.Argument(
                                                help=EXPERIMENT_FOLDER_HELP)]):
    _stage_limb(experiment_folder_path)


@app.command()
def align(
    experiment_folder_path: Annotated[
        str, typer.Argument(help="Path to the experiment folder")],
    morph: Annotated[
        bool,
        typer.Option(
            help="Automatically pick the isovalue for the surface")] = False):
    if morph:
        _morph_limb(experiment_folder_path)
    else:
        _rotate_limb(experiment_folder_path)


@app.command()
def vis(algorithm: VisAlgorithm, experiment_folder_path: Path,
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

    if algorithm == VisAlgorithm.slab:
        dynamic_slab(experiment_folder_path, channels[0])
