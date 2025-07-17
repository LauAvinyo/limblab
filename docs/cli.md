# Command-Line Interface (CLI) Reference

This document provides a comprehensive reference for the LimbLab Command-Line Interface (CLI). The CLI is designed for processing, analyzing, and visualizing 3D limb development data through a series of modular commands.

## Quick Start

The following is a typical workflow for processing a single experiment.

```bash
# Install LimbLab
pip install limblab

# 1. Initialize the experiment directory
limb create-experiment my_experiment

# 2. Process the raw data
limb clean-volume my_experiment/ raw_data.tif DAPI
limb extract-surface my_experiment/ --auto

# 3. Perform analysis
limb stage my_experiment/
limb align my_experiment/

# 4. Visualize the results
limb vis isosurfaces my_experiment/ DAPI
```

## Command Overview

| Command           | Description                                       |
|-------------------|---------------------------------------------------|
| `create-experiment` | Initializes a new experiment directory and structure. |
| `clean-volume`      | Applies filters to process raw volumetric data.      |
| `extract-surface`   | Generates a 3D surface mesh from a volume.        |
| `stage`             | Determines the developmental stage of a limb.      |
| `align`             | Aligns a sample to a reference template.          |
| `vis`               | Accesses various visualization algorithms.        |

---

## Detailed Command Reference

### `create-experiment`

Initializes a new experiment directory with a `pipeline.log` file for tracking processing steps and metadata.

**Usage**
```bash
limb create-experiment EXPERIMENT_NAME [PARENT_PATH]
```

**Arguments**

- `EXPERIMENT_NAME` (required): The name for the new experiment directory.
- `PARENT_PATH` (optional): The filesystem path where the experiment directory will be created. Defaults to the current working directory.

**Initial Configuration**

Upon execution, the command will prompt for essential metadata to be stored in `pipeline.log`:

- **Limb side:** `L` (Left) or `R` (Right).
- **Limb position:** `F` (Forelimb) or `H` (Hindlimb).
- **Microscope spacing:** Voxel size in micrometers, formatted as `X Y Z`.

---

### `clean-volume`

Processes a raw volume file by applying a standard image processing pipeline.

**Usage**

```bash
limb clean-volume EXPERIMENT_PATH VOLUME_PATH CHANNEL_NAME [OPTIONS]
```

**Arguments**

- `EXPERIMENT_PATH` (required): Path to the target experiment directory.
- `VOLUME_PATH` (required): Path to the raw input volume file (e.g., `.tif`).
- `CHANNEL_NAME` (required): A name for the data channel being processed (e.g., `DAPI`, `SOX9`).

**Options**

- `--sigma TEXT`: Sigma for Gaussian smoothing, formatted as `'x,y,z'`. Default: `'6,6,6'`.
- `--cutoff FLOAT`: Frequency cutoff for the low-pass filter. Default: `0.05`.
- `--size TEXT`: Output volume dimensions, formatted as `'x,y,z'`. Default: `'512,512,296'`.

**Methodology**

The command executes the following pipeline:

1.  Loads the raw volume and applies the voxel spacing defined in `pipeline.log`.
2.  Prompts for interactive thresholding to segment the primary signal from background noise.
3.  Clips the volume based on the selected intensity thresholds.
4.  Applies a Gaussian filter to reduce high-frequency noise.
5.  Applies a low-pass Fast Fourier Transform (FFT) filter to remove high-frequency artifacts.
6.  Resizes the volume to the specified output dimensions.
7.  Mirrors the volume along the appropriate axis if it is a left limb to standardize orientation.
8.  Saves the processed volume to the experiment directory and updates `pipeline.log`.

---

### `extract-surface`

Generates a 3D polygonal surface mesh from a processed DAPI volume.

**Usage**

```bash
limb extract-surface EXPERIMENT_PATH [ISOVALUE] [OPTIONS]
```

**Arguments**

- `EXPERIMENT_PATH` (required): Path to the experiment directory.
- `ISOVALUE` (optional): A specific isovalue to use for surface generation. If omitted, an interactive prompt will be shown.

**Options**

- `--auto / --no-auto`: If specified, automatically determines the optimal isovalue. Default is `--no-auto`.

**Methodology**

1.  Loads the cleaned DAPI volume from the experiment directory.
2.  Determines the intensity threshold (isovalue) for the surface, either automatically, from user input, or via an interactive slider.
3.  Generates a polygonal mesh of the isosurface using the marching cubes algorithm.
4.  Applies mesh decimation to reduce the polygon count for performance optimization.
5.  Saves the output mesh as a `.vtk` file in the experiment directory.

---

### `stage`

Determines the developmental stage of the limb by comparing its morphology to a reference database.

**Usage**
```bash
limb stage EXPERIMENT_PATH
```

**Arguments**

- `EXPERIMENT_PATH` (required): Path to the experiment directory.

**Methodology**

1.  Loads the 3D surface mesh.
2.  Opens an interactive 3D viewer where the user places points along the limb's proximal-distal axis.
3.  Fits a B-spline to the user-defined points to model the limb's central axis.
4.  Calculates the developmental stage by comparing morphological features derived from the spline against an internal reference database.
5.  Saves the staging results to `staging.txt` in the experiment directory.

**Interactive Controls**

- **Left-click:** Add a point.
- **Right-click:** Remove the last added point.
- **'c':** Clear all points.
- **'s':** Calculate the stage.
- **'r':** Reset the camera view.
- **'q':** Quit the interactive window.

---

### `align`

Aligns the limb surface with a reference template of the corresponding stage.

**Usage**
```bash
limb align EXPERIMENT_PATH [OPTIONS]
```

**Arguments**

- `EXPERIMENT_PATH` (required): Path to the experiment directory.

**Options**

- `--morph / --no-morph`: If specified, performs a non-linear morphing registration. Default is `--no-morph` (linear transformation).

**Alignment Methods**

-   **Linear Transformation (Default):** Performs a rigid transformation (rotation, translation, and uniform scaling) to align the principal axes of the sample with the reference template. This is suitable for gross alignment.
-   **Non-Linear Morphing (`--morph`):** Performs a non-rigid, deformable registration to precisely match the sample's surface morphology to the reference template. This method is computationally more intensive but provides higher accuracy for detailed comparative analyses.

---

### `vis`

Provides access to multiple visualization algorithms for data inspection and analysis.

**Usage**
```bash
limb vis ALGORITHM EXPERIMENT_PATH CHANNELS... [OPTIONS]
```

**Arguments**

- `ALGORITHM` (required): The visualization algorithm to use (e.g., `isosurfaces`, `raycast`).
- `EXPERIMENT_PATH` (required): Path to the experiment directory.
- `CHANNELS...` (required): One or more channel names to visualize.

**Available Algorithms**

#### `isosurfaces`
Generates one or more 3D isosurfaces at specified intensity thresholds from volumetric data. Suitable for visualizing gene expression domains.

**Usage**
`limb vis isosurfaces EXPERIMENT_PATH CHANNEL_1 [CHANNEL_2] ...`

#### `raycast`
Performs direct volume rendering using a raycasting algorithm. This allows for visualization of the entire data volume with user-defined transfer functions for color and opacity.

**Usage**
`limb vis raycast EXPERIMENT_PATH CHANNEL`

#### `slab`
Generates a 3D view of a thick, movable slice ("slab") through the volume data, allowing for inspection of internal structures.

**Usage**
`limb vis slab EXPERIMENT_PATH CHANNEL`

#### `slices`
Displays orthogonal 2D slices (sagittal, coronal, transverse) of one or more channels.

**Usage**
`limb vis slices EXPERIMENT_PATH CHANNEL_1 [CHANNEL_2] ...`

#### `probe`
Opens an interactive 3D view where a probe can be moved through the volume to measure and plot intensity values from multiple channels at specific points.

**Usage**
`limb vis probe EXPERIMENT_PATH CHANNEL_1 [CHANNEL_2] ...`

---

## Scripting and Automation

### Batch Processing
For simple batch operations, standard shell commands can be used to iterate over multiple experiment directories.

```bash
# Example: Stage all experiments in a directory
for exp in /path/to/experiments/*/; do
    limb stage "$exp"
done
```

### Python Scripting
For more complex workflows, LimbLab's CLI commands can be orchestrated from Python scripts using the `subprocess` module. This allows for programmatic control over the pipeline execution. For more granular control, consider using the underlying Python API.

```python
import subprocess
from pathlib import Path

def run_pipeline(exp_dir: Path, volume_file: Path, channel_name: str):
    """
    Example script to run a basic processing pipeline.
    """
    if not exp_dir.exists():
        subprocess.run(['limb', 'create-experiment', exp_dir.name, exp_dir.parent])

    # Clean volume, extract surface, and stage
    subprocess.run(['limb', 'clean-volume', str(exp_dir), str(volume_file), channel_name])
    subprocess.run(['limb', 'extract-surface', str(exp_dir), '--auto'])
    subprocess.run(['limb', 'stage', str(exp_dir)])

```
