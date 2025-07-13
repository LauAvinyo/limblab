"""
LimbLab Command Line Interface

This module provides the command-line interface for the LimbLab library,
enabling automated processing and analysis of limb development data.

The CLI supports the complete pipeline from raw data to visualization:
1. Create experiment structure
2. Clean and preprocess volume data
3. Extract 3D surfaces
4. Stage limbs using interactive tools
5. Align with reference templates
6. Visualize results

For detailed usage examples, see the README or run: limb --help
"""

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
from limblab.visualizations import (dynamic_slab, one_channel_isosurface,
                                      probe, raycast, slices,
                                      two_chanel_isosurface, arbitary_slice)

app = typer.Typer()

# Help text for experiment folder argument
EXPERIMENT_FOLDER_HELP = "Path to the experiment folder containing pipeline.log and processed data"


class VisAlgorithm(str, Enum):
    isosurfces = "isosurfaces"
    raycast = "raycast"
    slab = "slab"
    slices = "slices"
    probe = "probe"


@app.command()
def create_experiment(
    experiment_name: str,
    experiment_folder_path: Optional[str] = None
):
    """
    Create a new experiment folder with initial pipeline structure.
    
    This command creates a new experiment directory with the necessary
    folder structure and initializes the pipeline.log file for tracking
    processing steps.
    
    Args:
        experiment_name: Name of the experiment (will create folder with this name)
        experiment_folder_path: Parent directory where to create the experiment (default: current directory)
    
    Example:
        >>> limb create-experiment my_experiment
        >>> limb create-experiment my_experiment /path/to/experiments/
    """
    if experiment_folder_path is None:
        experiment_folder_path = "./"
    _create_experiment(experiment_folder_path, experiment_name)
    print(
        f"This will create the experiment folder {experiment_name} on path {experiment_folder_path}"
    )


@app.command()
def clean_volume(
    experiment_folder_path: Path, 
    volume_path: Path,
    channel_name: str,
    gaussian_sigma: Optional[str] = typer.Option(None, "--sigma", help="Gaussian smoothing parameters as 'x,y,z' (default: '6,6,6')"),
    frequency_cutoff: Optional[float] = typer.Option(None, "--cutoff", help="Frequency cutoff for low-pass filtering (default: 0.05)"),
    low_res_size: Optional[str] = typer.Option(None, "--size", help="Output volume size as 'x,y,z' (default: '512,512,296')")
):
    """
    Clean and preprocess volume data for analysis.
    
    This command processes raw volume data by applying thresholding, smoothing,
    and filtering operations. The cleaned volume is saved to the experiment folder.
    
    Args:
        experiment_folder_path: Path to the experiment folder
        volume_path: Path to the raw volume file (.tif format)
        channel_name: Channel name (e.g., 'DAPI', 'GFP', 'RFP')
        gaussian_sigma: Gaussian smoothing parameters as 'x,y,z' (default: '6,6,6')
        frequency_cutoff: Frequency cutoff for low-pass filtering (default: 0.05)
        low_res_size: Output volume size as 'x,y,z' (default: '512,512,296')
    
    Example:
        >>> limb clean-volume ./experiment raw_data.tif DAPI
        >>> limb clean-volume ./experiment raw_data.tif GFP --sigma 8,8,8 --cutoff 0.03
    """
    
    # Parse tuple parameters
    parsed_sigma = None
    if gaussian_sigma:
        try:
            parsed_sigma = tuple(float(x.strip()) for x in gaussian_sigma.split(','))
        except ValueError:
            typer.echo("Error: gaussian_sigma must be in format 'x,y,z'", err=True)
            raise typer.Exit(1)
    
    parsed_size = None
    if low_res_size:
        try:
            parsed_size = tuple(int(x.strip()) for x in low_res_size.split(','))
        except ValueError:
            typer.echo("Error: low_res_size must be in format 'x,y,z'", err=True)
            raise typer.Exit(1)
    
    _clean_volume(experiment_folder_path, volume_path, channel_name, 
                 gaussian_sigma=parsed_sigma, frequency_cutoff=frequency_cutoff, low_res_size=parsed_size)


@app.command()
def extract_surface(
    experiment_folder_path: Path = typer.Argument(help="Path to the experiment folder"),
    isovalue: Optional[int] = None,
    auto: bool = typer.Option(False, help="Automatically determine isovalue from volume histogram")
):
    """
    Extract 3D surface mesh from volume data.
    
    This command creates a 3D surface mesh from the DAPI volume using isosurface
    extraction. The surface is decimated for optimization and saved as a VTK file.
    
    Args:
        experiment_folder_path: Path to the experiment folder
        isovalue: Specific isovalue for surface extraction (if None, will be determined)
        auto: Automatically determine isovalue from volume histogram
    
    Example:
        >>> limb extract-surface ./experiment
        >>> limb extract-surface ./experiment 200
        >>> limb extract-surface ./experiment --auto
    """
    _extract_surface(experiment_folder_path, isovalue, auto)


@app.command()
def stage(experiment_folder_path: Path = typer.Argument(help=EXPERIMENT_FOLDER_HELP)):
    """
    Stage the limb using interactive 3D spline fitting.
    
    This command opens an interactive 3D viewer where you can place points
    along the limb to create a spline. The spline is used to determine
    the limb stage via online API or local executable.
    
    Args:
        experiment_folder_path: Path to the experiment folder
    
    Interactive Controls:
        - Click to add points along the limb
        - Right-click to remove points
        - Press 'c' to clear all points
        - Press 's' to stage the limb
        - Press 'r' to reset camera
        - Press 'q' to quit
    
    Example:
        >>> limb stage ./experiment
    """
    _stage_limb(experiment_folder_path)


@app.command()
def align(
    experiment_folder_path: str = typer.Argument(help="Path to the experiment folder"),
    morph: bool = typer.Option(False, help="Perform non-linear morphing instead of rotation")
):
    """
    Align the limb with reference template.
    
    This command aligns the limb with a reference template of the same stage.
    By default, it performs rigid body transformation (rotation/translation).
    With --morph flag, it performs non-linear morphing for better alignment.
    
    Args:
        experiment_folder_path: Path to the experiment folder
        morph: Perform non-linear morphing instead of rotation
    
    Example:
        >>> limb align ./experiment
        >>> limb align ./experiment --morph
    """
    if morph:
        _morph_limb(experiment_folder_path)
    else:
        _rotate_limb(experiment_folder_path)


@app.command()
def vis(algorithm: VisAlgorithm, experiment_folder_path: Path,
        channels: List[str]):
    """
    Visualize processed data using various algorithms.
    
    This command provides different visualization methods for the processed
    limb data, including isosurfaces, raycasting, slices, and more.
    
    Args:
        algorithm: Visualization algorithm to use
            - isosurfaces: 3D surface rendering (1-2 channels)
            - raycast: Volume raycasting (1 channel)
            - slab: Dynamic slab visualization (1 channel)
            - slices: 2D slice visualization (1-2 channels)
            - probe: Interactive probe visualization (multiple channels)
        experiment_folder_path: Path to the experiment folder
        channels: List of channel names to visualize (e.g., ['DAPI', 'GFP'])
    
    Example:
        >>> limb vis isosurfaces ./experiment DAPI
        >>> limb vis isosurfaces ./experiment DAPI GFP
        >>> limb vis raycast ./experiment DAPI
        >>> limb vis slices ./experiment DAPI GFP
    """
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
        if len(channels) == 2:
            arbitary_slice(experiment_folder_path, *channels)
        elif len(channels) == 1:
            slices(experiment_folder_path, channels[0])
        else:
            raise NotImplementedError
        
    if algorithm == VisAlgorithm.slices:
        slices(experiment_folder_path, channels[0])

    if algorithm == VisAlgorithm.probe:
        probe(experiment_folder_path, channels)

    if algorithm == VisAlgorithm.slab:
        dynamic_slab(experiment_folder_path, channels[0])
