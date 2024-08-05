# Clean Volume CLI Tool

This document provides detailed technical information on the `clean_volume` function. The function called by the CLI command:
```sh
limb clean-volume <folder_path> <volume_path> <channel_name>
```


## The function: `clean_volume`

**TLDR;** The `clean_volume` function processes raw volume data by performing a series of steps including loading pipeline configurations, applying filters, resizing, and saving the cleaned volume. This function is essential for preparing volume data for subsequent steps. You must use it. Also, depending on your raw data format, you may reduce a lot the size of the file. 

### Parameters

- **experiment_folder_path (Path)**: The directory path where the experiment data and configurations are stored.
- **volume_path (Path)**: The path to the raw volume file that needs to be processed.
- **channel_name (str)**: The name of the channel to be processed, typically representing a specific staining or imaging channel.

### Workflow

First of it converts the channel name to uppercase for consistency (as you may have seen in the pipeline.log files). Then, it reads the pipeline configuration from the `experiment_folder_path`. We need the parameters `SIDE` (indicating the anatomical side of the limb) and `SPACING` (voxel spacing).  We set the constants: the Gaussian smoothing (`SIGMA`) to (6, 6, 6), frequency cutoff (`CUTOFF`) to 0.05, and volume size to (512, 512, 296). For now, the values are set, but it's plan passed as parameters in future releases. 

The raw volume file is loaded into memory for processing, and the voxel spacing is applied to ensure accurate dimensional representation. Then and interactive tool popups to allow users to select bottom and top isovalues for thresholding, which determine the intensity range to be preserved in the volume. The volume is then thresholded based on the selected isovalues, replacing out-of-range values and resizing the volume to the specified dimensions. If the volume corresponds to the left side (`SIDE == "L"`), it mirrors the volume for symmetry. Gaussian smoothing and frequency pass filtering are applied to reduce noise and remove high-frequency artifacts.

Finally, the processed volume is written to disk, and the pipeline configuration is updated with metadata, including the processed volume path and selected isovalues. The updated pipeline configuration is saved back to the `experiment_folder_path`.

### Example Usage

You could use the helper function on its own: 

```python
from pathlib import Path

# Define paths and channel
experiment_folder_path = Path("/path/to/experiment")
volume_path = Path("/path/to/raw_volume.tif")
channel_name = "dapi"

# Clean the volume
_clean_volume(experiment_folder_path, volume_path, channel_name)
```