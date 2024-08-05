# Align CLI Tool

This document provides detailed technical information on the `align` function, which is executed using the CLI command:

```sh
limb align <folder_path> [--morph]
```

**TLDR;**  In essence, the `align` function is designed to align a 3D surface mesh of a limb with a reference model through either rotation or morphing, depending on the presence of the `--morph` flag. If the `--morph` flag is set, the function performs a morphing alignment; otherwise, it defaults to a rotational alignment. We use this functionality to ensyre that the limb model aligns accurately with a reference model, which is essential for detailed analysis and comparison.

### Detailed Workflow

When you invoke the `align` function, it determines the alignment method based on the `morph` parameter.

#### Rotation Alignment

For rotational alignment, the function delegates the task to `_rotate_limb`. This process begins by loading the pipeline configuration from the experiment folder and retrieving the path to the surface mesh and the stage information. If the staging algorithm has not been completed, the function will prompt you to run it first. 

Next, the function fetches the reference limb corresponding to the current stage. It then loads the source and target meshes for visualization, allowing manual alignment through interactive adjustments. This manual alignment enables you to ensure that the limb model matches the reference model as closely as possible. The function computes a transformation matrix based on your adjustments and saves this matrix to disk. It then updates the pipeline configuration with this transformation matrix and the rotation details.

#### Morphing Alignment

If the `--morph` flag is used, the function invokes `_morph_limb` instead. This process similarly starts by loading the pipeline configuration and retrieving the surface mesh and stage information. The function checks to ensure that the staging algorithm has been executed. If not, it prompts you to run it before proceeding.

The function then retrieves the reference limb for the current stage and uses a morphing tool to calculate the transformation required to align the source mesh with the reference model. This morphing transformation adjusts the mesh to fit the reference model more accurately. Once the transformation is computed, it is saved to disk, and the pipeline configuration is updated with the new morphing information.

### Example Usage

To perform a rotational alignment programmatically, you can use the following code:

```python
from pathlib import Path

# Define the path to the experiment folder
experiment_folder_path = Path("/path/to/experiment")

# Execute the function to perform rotational alignment
_rotate_limb(experiment_folder_path)
```

For morphing alignment, the code would look like this:

```python
from pathlib import Path

# Define the path to the experiment folder
experiment_folder_path = Path("/path/to/experiment")

# Execute the function to perform morphing alignment
_morph_limb(experiment_folder_path)
```