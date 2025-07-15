# LimbLab Command Line Interface

The LimbLab CLI provides a powerful command-line interface for processing and analyzing 3D limb development data. This guide covers all available commands with detailed explanations, examples, and best practices.

## Quick Start

```bash
# Install LimbLab
pip install limb

# Create your first experiment
limb create-experiment my_experiment

# Process your data
limb clean-volume my_experiment raw_data.tif DAPI
limb extract-surface my_experiment --auto
limb stage my_experiment
limb align my_experiment

# Visualize results
limb vis isosurfaces my_experiment DAPI
```

## Command Overview

| Command | Description | Usage |
|---------|-------------|-------|
| `create-experiment` | Initialize new experiment | `limb create-experiment NAME [PATH]` |
| `clean-volume` | Process raw volume data | `limb clean-volume PATH VOLUME CHANNEL [OPTIONS]` |
| `extract-surface` | Create 3D surface mesh | `limb extract-surface PATH [ISOVALUE] [OPTIONS]` |
| `stage` | Determine limb stage | `limb stage PATH` |
| `align` | Align with reference | `limb align PATH [OPTIONS]` |
| `vis` | Visualize data | `limb vis ALGORITHM PATH CHANNELS...` |

---

## Detailed Command Reference

### `create-experiment`

Creates a new experiment directory with initial pipeline structure.

**Usage:**
```bash
limb create-experiment EXPERIMENT_NAME [EXPERIMENT_FOLDER_PATH]
```

**Arguments:**
- `EXPERIMENT_NAME` (required): Name of the experiment
- `EXPERIMENT_FOLDER_PATH` (optional): Parent directory (default: current directory)

**Interactive prompts:**
- **Limb side:** L (Left) or R (Right)
- **Limb position:** F (Forelimb) or H (Hindlimb)
- **Microscope spacing:** X Y Z values in micrometers

**Examples:**
```bash
# Create in current directory
limb create-experiment hoxa11_analysis

# Create in specific directory
limb create-experiment sox9_study ./experiments/

# Create with full path
limb create-experiment bmp2_analysis /path/to/experiments/
```

```
hoxa11_analysis/
├── pipeline.log          # Experiment configuration
└── README.md            # Experiment notes
```

---

### `clean-volume`

Processes raw volume data by applying filtering, smoothing, and thresholding.

**Usage:**
```bash
limb clean-volume EXPERIMENT_FOLDER_PATH VOLUME_PATH CHANNEL_NAME [OPTIONS]
```

**Arguments:**
- `EXPERIMENT_FOLDER_PATH` (required): Path to experiment directory
- `VOLUME_PATH` (required): Path to raw volume file (.tif format)
- `CHANNEL_NAME` (required): Channel name (e.g., DAPI, GFP, RFP)

**Options:**
- `--sigma TEXT`: Gaussian smoothing parameters as 'x,y,z' (default: '6,6,6')
- `--cutoff FLOAT`: Frequency cutoff for low-pass filtering (default: 0.05)
- `--size TEXT`: Output volume size as 'x,y,z' (default: '512,512,296')

**Processing steps:**
1. **Load raw volume** and apply voxel spacing
2. **Interactive thresholding** (select bottom and top isovalues)
3. **Volume clipping** based on selected thresholds
4. **Gaussian smoothing** to reduce noise
5. **Frequency filtering** to remove artifacts
6. **Volume resizing** for optimization
7. **Mirroring** (if left side limb)
8. **Save cleaned volume** and update pipeline

**Examples:**
```bash
# Basic volume cleaning
limb clean-volume ./experiment raw_data.tif DAPI

# Custom parameters
limb clean-volume ./experiment raw_data.tif GFP \
  --sigma 8,8,8 \
  --cutoff 0.03 \
  --size 1024,1024,296

# High-resolution processing
limb clean-volume ./experiment raw_data.tif RFP \
  --size 2048,2048,592
```


---

### `extract-surface`

Creates a 3D surface mesh from the cleaned DAPI volume.

**Usage:**
```bash
limb extract-surface EXPERIMENT_FOLDER_PATH [ISOVALUE] [OPTIONS]
```

**Arguments:**
- `EXPERIMENT_FOLDER_PATH` (required): Path to experiment directory
- `ISOVALUE` (optional): Specific isovalue for surface extraction

**Options:**
- `--auto / --no-auto`: Automatically determine isovalue (default: no-auto)

**Surface extraction process:**
1. **Load cleaned DAPI volume**
2. **Isovalue selection** (interactive or automatic)
3. **Marching cubes algorithm** for surface generation
4. **Mesh decimation** for performance optimization
5. **Save VTK surface file**

**Examples:**
```bash
# Interactive isovalue selection
limb extract-surface ./experiment

# Automatic isovalue determination
limb extract-surface ./experiment --auto

# Specific isovalue
limb extract-surface ./experiment 200
```

**Interactive controls:**
- **Mouse:** Adjust isovalue slider
- **Preview:** Real-time surface visualization
- **Accept:** Confirm surface quality


---

### `stage`

Determines the developmental stage of the limb using interactive 3D spline fitting.

**Usage:**
```bash
limb stage EXPERIMENT_FOLDER_PATH
```

**Arguments:**
- `EXPERIMENT_FOLDER_PATH` (required): Path to experiment directory

**Staging process:**
1. **Load 3D surface mesh**
2. **Interactive point placement** along limb axis
3. **Spline fitting** through placed points
4. **Stage calculation** using reference database
5. **Save staging results**

**Interactive controls:**
- **Left click:** Add point
- **Right click:** Remove point
- **'c':** Clear all points
- **'s':** Stage the limb
- **'r':** Reset camera
- **'q':** Quit

**Staging guidelines:**
- **Point placement:** Along proximal-distal axis
- **Focus area:** Digit-forming regions
- **Number of points:** 10 points recommended
- **Distribution:** Even spacing along limb

**Examples:**
```bash
# Basic staging
limb stage ./experiment
```

---

### `align`

Aligns the limb with a reference template for comparative analysis.

**Usage:**
```bash
limb align EXPERIMENT_FOLDER_PATH [OPTIONS]
```

**Arguments:**
- `EXPERIMENT_FOLDER_PATH` (required): Path to experiment directory

**Options:**
- `--morph / --no-morph`: Perform non-linear morphing (default: no-morph)

**Alignment methods:**

#### Linear Transformation (Default)
- **Rotation:** Manual 3D rotation
- **Scaling:** Uniform scaling
- **Translation:** Position adjustment
- **Use case:** Basic alignment, rigid transformations

#### Non-Linear Morphing (--morph)
- **Deformation:** Complex shape matching
- **Higher accuracy:** Better for detailed analysis
- **Computational cost:** More intensive
- **Use case:** Precise alignment, comparative studies

**Interactive controls:**
- **Mouse:** Rotate, pan, zoom
- **'a':** Apply transformation
- **'r':** Reset alignment
- **Close window:** Save transformation

**Examples:**
```bash
# Linear transformation
limb align ./experiment

# Non-linear morphing
limb align ./experiment --morph
```


### `vis`

Creates various types of visualizations from processed data.

**Usage:**
```bash
limb vis ALGORITHM EXPERIMENT_FOLDER_PATH CHANNELS... [OPTIONS]
```

**Arguments:**
- `ALGORITHM` (required): Visualization algorithm
- `EXPERIMENT_FOLDER_PATH` (required): Path to experiment directory
- `CHANNELS...` (required): Channel names to visualize

**Available algorithms:**

#### `isosurfaces`
Creates 3D surface renderings of gene expression.

**Usage:**
```bash
limb vis isosurfaces EXPERIMENT_FOLDER_PATH CHANNEL [CHANNEL2] [OPTIONS]
```

**Features:**
- **Single channel:** Grayscale or color mapping
- **Dual channel:** Red-Green overlay
- **Multi-channel:** Multiple color channels
- **Interactive:** Real-time parameter adjustment

**Examples:**
```bash
# Single channel
limb vis isosurfaces ./experiment GENE

# Dual channel
limb vis isosurfaces ./experiment SOX9 BMP2
```

#### `raycast`
Creates volume renderings using raycasting.

**Usage:**
```bash
limb vis raycast EXPERIMENT_FOLDER_PATH CHANNEL [OPTIONS]
```

**Features:**
- **Volume rendering:** Full 3D volume visualization
- **Transfer functions:** Custom opacity mapping
- **Advanced lighting:** Realistic illumination
- **Depth cues:** Enhanced depth perception

**Examples:**
```bash
# Basic raycasting
limb vis raycast ./experiment GENE
```

#### `slab`
Creates dynamic slab visualizations.

**Usage:**
```bash
limb vis slab EXPERIMENT_FOLDER_PATH CHANNEL [OPTIONS]
```

**Features:**
- **Dynamic slicing:** Adjustable slab thickness
- **Position control:** Move through volume
- **Real-time:** Interactive parameter adjustment
- **Export:** Save current view

**Examples:**
```bash
# Dynamic slab
limb vis slab ./experiment GENE
```

#### `slices`
Creates 2D slice visualizations.

**Usage:**
```bash
limb vis slices EXPERIMENT_FOLDER_PATH CHANNEL [CHANNEL2] [OPTIONS]
```

**Features:**
- **Multiple views:** Sagittal, coronal, transverse
- **Dual channel:** Overlay visualization
- **Interactive:** Real-time slice positioning
- **Quantitative:** Expression measurement tools

**Examples:**
```bash
# Single channel slice
limb vis slices ./experiment GENE

# Dual channel slice
limb vis slices ./experiment SOX9 BMP2
```

#### `probe`
Creates interactive probe visualizations.

**Usage:**
```bash
limb vis probe EXPERIMENT_FOLDER_PATH CHANNELS... [OPTIONS]
```

**Features:**

**Examples:**
```bash
# Multi-channel probe
limb vis probe ./experiment SOX9 BMP2
```
---

## 🔧 Advanced Usage

### Batch Processing

Process multiple experiments efficiently:

```bash
# Stage multiple experiments
for exp in experiments/*/; do
    limb stage "$exp"
done
```

### Integration with Scripts

Integrate LimbLab commands into Python scripts:

```python
import subprocess

def process_experiment(exp_path, volume_path, channel):
    # Create experiment
    subprocess.run(['limb', 'create-experiment', exp_path])
    
    # Clean volume
    subprocess.run(['limb', 'clean-volume', exp_path, volume_path, channel])
    
    # Extract surface
    subprocess.run(['limb', 'extract-surface', exp_path, '--auto'])
    
    # Stage limb
    subprocess.run(['limb', 'stage', exp_path])
```

---

## 📊 Output and Results

### File Structure

After running the pipeline, your experiment directory will contain:

```
experiment/
├── pipeline.log                    # Processing log
├── *_cleaned.tif                   # Cleaned volumes
├── *_surface.vtk                   # 3D surface mesh
├── staging.txt                     # Staging results
├── transformation_matrix.txt       # Alignment data
├── visualizations/                 # Generated images
│   ├── isosurface.png
│   ├── slice.png
│   └── probe_data.csv
└── README.md                       # Experiment notes
```

### Pipeline Log

The `pipeline.log` file tracks all processing steps:

```txt
BASE ./experiment
SIDE L
POSITION H
SPACING 0.65 0.65 2.0
DAPI ./dapi_cleaned.tif
SURFACE ./dapi_surface.vtk
STAGE 25.3
TRANSFORMATION ./transformation_matrix.txt
```

---

*The LimbLab CLI provides a powerful and flexible interface for 3D limb data analysis. With practice and experimentation, you'll develop efficient workflows tailored to your specific research needs.*
