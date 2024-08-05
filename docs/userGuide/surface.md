# Surface Extraction 


# Extract Surface CLI Tool

This document provides detailed technical information on the `extract_surface` function. The function is invoked by the CLI command:

```sh
limb extract-surface <folder_path> [isovalue] [--auto]
```

## The function: `extract_surface`

**TLDR;** The `extract_surface` function extracts a 3D surface from a volume dataset based on an isovalue. You can specify the isovalue manually or let the function automatically determine it based on the volume data. The function processes the volume data, extracts the surface, decimates it to reduce complexity, and saves the result. This function is vital for generating surface representations of volumetric data.

### Parameters

- **experiment_folder_path (Path)**: The path to the directory where the experiment data and configurations are stored.
- **isovalue (Optional[int])**: A specific isovalue to use for extracting the surface. If not provided, the function will either compute it automatically or prompt the user for selection.
- **auto (bool)**: If set to `True`, the function will automatically determine the isovalue from the volume data. If `False` and no isovalue is provided, the user will be prompted to select one interactively.

### Workflow

The function starts by loading the pipeline configuration from the `experiment_folder_path`. It checks for the existence of the DAPI volume, which is required for processing. If the volume is missing, an error message is displayed, and the function terminates. You will have to go back and clean it. 

The function then locates the DAPI volume file and loads it into memory. If an isovalue is provided as an argument, it is used directly. If the `auto` flag is set and no isovalue is provided, the function calculates an automatic isovalue by analyzing the volume's histogram. The histogram's mean value is used as the isovalue for surface extraction. If neither an isovalue nor the `auto` flag is provided, an interactive tool (`IsosurfaceBrowser`) is launched to allow the user to select an isovalue manually. The selected value is displayed for confirmation.

Once the isovalue is determined, the function proceeds to compute the isosurface using the specified value. The surface is then processed to extract the largest connected region and decimated to reduce the number of points and improve efficientcy down the line.

The decimated surface is saved to a file with the suffix `_surface.vtk`, and the path to this file is updated in the pipeline configuration. The updated pipeline configuration is saved back to the `pipeline.log` file in the experiment folder.

### Example Usage

You could use the `extract_surface` function programmatically as follows:

```python
from pathlib import Path

# Define paths and options
experiment_folder_path = Path("/path/to/experiment")
isovalue = 150  # Optional: specify an isovalue or leave as None
auto = True  # Set to True for automatic isovalue detection

# Extract the surface
_extract_surface(experiment_folder_path, isovalue, auto)
```
