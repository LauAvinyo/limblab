# LimbLab Command Line Interface

The LimbLab CLI provides a powerful command-line interface for processing and analyzing 3D limb development data. This guide covers all available commands with detailed explanations, examples, and best practices.

## 🚀 Quick Start

```bash
# Install LimbLab
pip install limblab

# Create your first experiment
limblab create-experiment my_experiment

# Process your data
limblab clean-volume my_experiment raw_data.tif DAPI
limblab extract-surface my_experiment --auto
limblab stage my_experiment
limblab align my_experiment

# Visualize results
limblab vis isosurfaces my_experiment DAPI
```

## 📋 Command Overview

| Command | Description | Usage |
|---------|-------------|-------|
| `create-experiment` | Initialize new experiment | `limblab create-experiment NAME [PATH]` |
| `clean-volume` | Process raw volume data | `limblab clean-volume PATH VOLUME CHANNEL [OPTIONS]` |
| `extract-surface` | Create 3D surface mesh | `limblab extract-surface PATH [ISOVALUE] [OPTIONS]` |
| `stage` | Determine limb stage | `limblab stage PATH` |
| `align` | Align with reference | `limblab align PATH [OPTIONS]` |
| `vis` | Visualize data | `limblab vis ALGORITHM PATH CHANNELS...` |

---

## 🔧 Detailed Command Reference

### `create-experiment`

Creates a new experiment directory with initial pipeline structure.

**Usage:**
```bash
limblab create-experiment EXPERIMENT_NAME [EXPERIMENT_FOLDER_PATH]
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
limblab create-experiment hoxa11_analysis

# Create in specific directory
limblab create-experiment sox9_study ./experiments/

# Create with full path
limblab create-experiment bmp2_analysis /path/to/experiments/
```

**Output:**
```
✅ Experiment created: ./hoxa11_analysis
📝 Pipeline log initialized
📁 Directory structure created
```

**Generated files:**
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
limblab clean-volume EXPERIMENT_FOLDER_PATH VOLUME_PATH CHANNEL_NAME [OPTIONS]
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
limblab clean-volume ./experiment raw_data.tif DAPI

# Custom parameters
limblab clean-volume ./experiment raw_data.tif GFP \
  --sigma 8,8,8 \
  --cutoff 0.03 \
  --size 1024,1024,296

# High-resolution processing
limblab clean-volume ./experiment raw_data.tif RFP \
  --size 2048,2048,592
```

**Interactive workflow:**
1. **Histogram display:** Shows intensity distribution
2. **Threshold selection:** Click to set bottom/top values
3. **Preview:** Review cleaned volume
4. **Confirmation:** Accept or adjust parameters

**Expected output:**
```
📊 Loading volume: raw_data.tif
🎯 Channel: DAPI
📏 Voxel spacing: 0.65 0.65 2.0 μm
🔧 Processing with sigma=(6,6,6), cutoff=0.05
✅ Volume cleaned and saved
📊 Size reduced: 1.2GB → 240MB
📝 Pipeline log updated
```

---

### `extract-surface`

Creates a 3D surface mesh from the cleaned DAPI volume.

**Usage:**
```bash
limblab extract-surface EXPERIMENT_FOLDER_PATH [ISOVALUE] [OPTIONS]
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
limblab extract-surface ./experiment

# Automatic isovalue determination
limblab extract-surface ./experiment --auto

# Specific isovalue
limblab extract-surface ./experiment 200
```

**Interactive controls:**
- **Mouse:** Adjust isovalue slider
- **Preview:** Real-time surface visualization
- **Accept:** Confirm surface quality

**Expected output:**
```
🎯 Surface extraction started
📊 Using isovalue: 180
🔧 Generating surface with marching cubes
📊 Mesh: 15,432 vertices, 30,864 faces
💾 Saved as: experiment/dapi_surface.vtk
📝 Pipeline log updated
```

---

### `stage`

Determines the developmental stage of the limb using interactive 3D spline fitting.

**Usage:**
```bash
limblab stage EXPERIMENT_FOLDER_PATH
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
- **Number of points:** 5-10 points recommended
- **Distribution:** Even spacing along limb

**Examples:**
```bash
# Basic staging
limblab stage ./experiment

# Staging with specific reference
limblab stage ./experiment --reference hindlimb_stage25
```

**Expected output:**
```
🎯 Staging started
📊 Surface loaded: dapi_surface.vtk
🎮 Interactive viewer opened
📊 Points placed: 8
🎯 Stage determined: 25.3
📊 Confidence: 94.2%
💾 Results saved: experiment/staging.txt
```

**Generated files:**
```
experiment/
├── staging.txt              # Staging results
├── staging_points.txt       # Point coordinates
└── staging_fit.txt          # Spline fit data
```

---

### `align`

Aligns the limb with a reference template for comparative analysis.

**Usage:**
```bash
limblab align EXPERIMENT_FOLDER_PATH [OPTIONS]
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
limblab align ./experiment

# Non-linear morphing
limblab align ./experiment --morph

# Alignment with specific reference
limblab align ./experiment --reference stage25_hindlimb
```

**Expected output:**
```
🎯 Alignment started
📊 Reference template: stage25_hindlimb
🔧 Loading transformation tools
🎮 Interactive viewer opened
✅ Transformation applied
💾 Matrix saved: experiment/transformation.txt
📝 Pipeline log updated
```

---

### `vis`

Creates various types of visualizations from processed data.

**Usage:**
```bash
limblab vis ALGORITHM EXPERIMENT_FOLDER_PATH CHANNELS... [OPTIONS]
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
limblab vis isosurfaces EXPERIMENT_FOLDER_PATH CHANNEL [CHANNEL2] [OPTIONS]
```

**Features:**
- **Single channel:** Grayscale or color mapping
- **Dual channel:** Red-Green overlay
- **Multi-channel:** Multiple color channels
- **Interactive:** Real-time parameter adjustment

**Examples:**
```bash
# Single channel
limblab vis isosurfaces ./experiment DAPI

# Dual channel
limblab vis isosurfaces ./experiment SOX9 BMP2

# High resolution
limblab vis isosurfaces ./experiment HOXA11 --high-res
```

#### `raycast`
Creates volume renderings using raycasting.

**Usage:**
```bash
limblab vis raycast EXPERIMENT_FOLDER_PATH CHANNEL [OPTIONS]
```

**Features:**
- **Volume rendering:** Full 3D volume visualization
- **Transfer functions:** Custom opacity mapping
- **Advanced lighting:** Realistic illumination
- **Depth cues:** Enhanced depth perception

**Examples:**
```bash
# Basic raycasting
limblab vis raycast ./experiment DAPI

# Custom transfer function
limblab vis raycast ./experiment GFP --transfer-function custom
```

#### `slab`
Creates dynamic slab visualizations.

**Usage:**
```bash
limblab vis slab EXPERIMENT_FOLDER_PATH CHANNEL [OPTIONS]
```

**Features:**
- **Dynamic slicing:** Adjustable slab thickness
- **Position control:** Move through volume
- **Real-time:** Interactive parameter adjustment
- **Export:** Save current view

**Examples:**
```bash
# Dynamic slab
limblab vis slab ./experiment DAPI

# Fixed thickness
limblab vis slab ./experiment GFP --thickness 50
```

#### `slices`
Creates 2D slice visualizations.

**Usage:**
```bash
limblab vis slices EXPERIMENT_FOLDER_PATH CHANNEL [CHANNEL2] [OPTIONS]
```

**Features:**
- **Multiple views:** Sagittal, coronal, transverse
- **Dual channel:** Overlay visualization
- **Interactive:** Real-time slice positioning
- **Quantitative:** Expression measurement tools

**Examples:**
```bash
# Single channel slice
limblab vis slices ./experiment DAPI

# Dual channel slice
limblab vis slices ./experiment SOX9 BMP2

# Specific orientation
limblab vis slices ./experiment HOXA11 --orientation sagittal
```

#### `probe`
Creates interactive probe visualizations.

**Usage:**
```bash
limblab vis probe EXPERIMENT_FOLDER_PATH CHANNELS... [OPTIONS]
```

**Features:**
- **Point probes:** Single location measurements
- **Line probes:** Expression profiles
- **Volume probes:** Regional analysis
- **Data export:** CSV format output

**Examples:**
```bash
# Multi-channel probe
limblab vis probe ./experiment DAPI SOX9 BMP2

# Export data
limblab vis probe ./experiment HOXA11 --export-data

# Specific probe type
limblab vis probe ./experiment GFP --probe-type line
```

**Common options for all algorithms:**
- `--high-res`: Generate high-resolution output
- `--output PATH`: Specify output file path
- `--format FORMAT`: Output format (PNG, TIFF, PDF)
- `--colormap NAME`: Color scheme (viridis, plasma, inferno)

---

## 🔧 Advanced Usage

### Batch Processing

Process multiple experiments efficiently:

```bash
# Process multiple volumes
for volume in raw_data/*.tif; do
    limblab clean-volume experiment "$volume" DAPI
done

# Stage multiple experiments
for exp in experiments/*/; do
    limblab stage "$exp"
done
```

### Custom Parameters

Use custom parameters for specific applications:

```bash
# High-resolution processing
limblab clean-volume experiment data.tif DAPI \
  --sigma 12,12,12 \
  --cutoff 0.02 \
  --size 2048,2048,592

# Custom visualization
limblab vis isosurfaces experiment GENE \
  --high-res \
  --colormap plasma \
  --output custom_figure.png
```

### Integration with Scripts

Integrate LimbLab commands into Python scripts:

```python
import subprocess

def process_experiment(exp_path, volume_path, channel):
    # Create experiment
    subprocess.run(['limblab', 'create-experiment', exp_path])
    
    # Clean volume
    subprocess.run(['limblab', 'clean-volume', exp_path, volume_path, channel])
    
    # Extract surface
    subprocess.run(['limblab', 'extract-surface', exp_path, '--auto'])
    
    # Stage limb
    subprocess.run(['limblab', 'stage', exp_path])
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

## 🔧 Troubleshooting

### Common Issues

**1. Volume too large:**
```bash
# Reduce output size
limblab clean-volume experiment data.tif DAPI --size 256,256,148
```

**2. Poor surface quality:**
```bash
# Try automatic isovalue selection
limblab extract-surface experiment --auto

# Or use specific isovalue
limblab extract-surface experiment 150
```

**3. Staging fails:**
- Ensure points are placed along limb axis
- Use more points for better accuracy
- Check surface quality

**4. Alignment issues:**
- Start with gross alignment
- Use morphing for complex shapes
- Check reference template availability

### Performance Optimization

**For large datasets:**
- Use smaller output sizes
- Enable GPU acceleration when available
- Process in batches
- Monitor memory usage

**For high-resolution output:**
- Use `--high-res` flag
- Increase system memory
- Use SSD storage
- Close other applications

---

## 📚 Best Practices

### Workflow Recommendations

1. **Plan ahead:** Sketch your analysis workflow
2. **Use consistent naming:** Standardize file and directory names
3. **Document parameters:** Record all custom settings
4. **Version control:** Track changes to your data
5. **Backup regularly:** Keep copies of important data

### Data Organization

```
project/
├── raw_data/              # Original data
├── experiments/           # Processed experiments
│   ├── experiment1/
│   ├── experiment2/
│   └── experiment3/
├── references/            # Reference templates
├── results/               # Final results
└── documentation/         # Analysis notes
```

### Quality Control

- **Check data integrity:** Verify file sizes and formats
- **Review visualizations:** Ensure quality meets standards
- **Validate results:** Compare with known references
- **Document issues:** Record problems and solutions

---

## 🆘 Getting Help

### Command Help

```bash
# General help
limblab --help

# Command-specific help
limblab create-experiment --help
limblab clean-volume --help
limblab vis --help
```

### Documentation

- **User Guide:** Detailed explanations of each step
- **Tutorials:** Step-by-step examples
- **API Reference:** Python interface documentation
- **Examples:** Sample data and workflows

### Support

- **GitHub Issues:** Report bugs and request features
- **Discussion Forum:** Ask questions and share solutions
- **Email Support:** Contact the development team
- **Community:** Join user groups and workshops

---

*The LimbLab CLI provides a powerful and flexible interface for 3D limb data analysis. With practice and experimentation, you'll develop efficient workflows tailored to your specific research needs.*
