# Hoxa11 Gene Expression Analysis Tutorial

Welcome to the comprehensive guide for analyzing Hoxa11 gene expression using LimbLab! This tutorial will walk you through the complete pipeline for processing and visualizing 3D limb data with Hoxa11 expression.

## 🎯 Objective

The goal of this tutorial is to analyze Hoxa11 gene expression in mouse limb development using Hybridization Chain Reaction (HCR) data. Hoxa11 is a crucial gene involved in limb patterning and development. By analyzing it in 3D, we can gain insights that might be missed in traditional 2D projections.

**What you'll learn:**
- Setting up experiments in LimbLab
- Processing raw volume data
- Extracting 3D surfaces
- Staging limbs automatically
- Aligning with reference templates
- Creating publication-ready visualizations

## 📁 Data Overview

**Dataset:** Hoxa11 HCR expression data  
**Location:** `example_data/hoxa11_raw_data/`  
**Channels:** 
- DAPI (nuclear staining)
- Hoxa11 (gene expression)

**Files:**
- `HCR11_HOXA11_l1_dapi_488_LH.tif` - DAPI channel
- `HCR11_HOXA11_l1_hoxa11_647_LH.tif` - Hoxa11 channel

## 🚀 Step-by-Step Pipeline

### Step 1: Create Experiment Structure

First, we need to create a new experiment folder to keep our raw data safe and organized.

```bash
limblab create-experiment case_studies/hoxa11_pipeline
```

**What happens:** LimbLab creates a new directory structure and initializes a `pipeline.log` file to track all processing steps.

**Interactive prompts:**
- **Limb side:** Select `L` (Left)
- **Limb position:** Select `H` (Hindlimb) 
- **Microscope spacing:** Use default `0.65 0.65 2.0`

**Expected output:**
```
✅ Experiment created: case_studies/hoxa11_pipeline
📝 Pipeline log initialized
```

**Your `pipeline.log` should contain:**
```txt
BASE ./case_studies/hoxa11_pipeline
SIDE L
POSITION H
SPACING 0.65 0.65 2.0
```

---

### Step 2: Clean DAPI Volume

The DAPI channel provides the structural reference for the limb. We need to clean it to remove noise and artifacts.

```bash
limblab clean-volume case_studies/hoxa11_pipeline example_data/hoxa11_raw_data/HCR11_HOXA11_l1_dapi_488_LH.tif dapi
```

**What happens:** 
1. LimbLab loads the raw DAPI volume
2. An interactive plotter appears showing the volume histogram
3. You select threshold values to remove background noise
4. The volume is processed with smoothing and filtering

**Interactive steps:**
1. **Histogram analysis:** Examine the intensity distribution
2. **Threshold selection:** Click to set bottom and top isovalues
3. **Preview:** Review the cleaned volume
4. **Confirm:** Accept the processing parameters

**Processing details:**
- Gaussian smoothing: (6, 6, 6)
- Frequency cutoff: 0.05
- Output size: (512, 512, 296)
- Volume reduction: ~80% (typical)

**Expected result:**
```
✅ DAPI volume cleaned and saved
📊 Volume size reduced from 1.2GB to 240MB
📝 Pipeline log updated
```

---

### Step 3: Clean Hoxa11 Volume

Now we process the Hoxa11 gene expression channel using the same cleaning pipeline.

```bash
limblab clean-volume case_studies/hoxa11_pipeline example_data/hoxa11_raw_data/HCR11_HOXA11_l1_hoxa11_647_LH.tif hoxa11
```

**What happens:** Same cleaning process as DAPI, but optimized for gene expression data.

**Key differences:**
- Different threshold values (typically higher for gene expression)
- Same smoothing and filtering parameters
- Maintains spatial relationship with DAPI channel

**Expected result:**
```
✅ Hoxa11 volume cleaned and saved
📊 Gene expression preserved
📝 Pipeline log updated
```

---

### Step 4: Extract 3D Surface

We create a 3D surface mesh from the DAPI volume for further analysis and visualization.

```bash
limblab extract-surface case_studies/hoxa11_pipeline/
```

**What happens:**
1. LimbLab loads the cleaned DAPI volume
2. Interactive isovalue selection for surface extraction
3. Surface mesh generation using marching cubes algorithm
4. Mesh decimation for performance optimization

**Interactive steps:**
1. **Isovalue selection:** Choose the intensity threshold for surface
2. **Surface preview:** Review the generated mesh
3. **Quality check:** Ensure surface captures limb morphology

**Technical details:**
- Algorithm: Marching cubes
- Decimation: 0.5% of original points
- Format: VTK file
- File size: ~2-5MB

**Expected result:**
```
✅ Surface mesh extracted
📊 Mesh: 15,432 vertices, 30,864 faces
💾 Saved as: case_studies/hoxa11_pipeline/HCR11_HOXA11_l1_dapi_488_LH_surface.vtk
```

---

### Step 5: Stage the Limb

Determine the developmental stage of the limb using our automated staging algorithm.

```bash
limblab stage case_studies/hoxa11_pipeline/
```

**What happens:**
1. Interactive 3D viewer opens with the limb surface
2. You place points along the limb's long axis
3. A spline is fitted through the points
4. The algorithm calculates the developmental stage

**Interactive controls:**
- **Left click:** Add point
- **Right click:** Remove point  
- **'c':** Clear all points
- **'s':** Stage the limb
- **'r':** Reset camera
- **'q':** Quit

**Staging process:**
1. Place 5-10 points along the limb's proximal-distal axis
2. Focus on the digit-forming region
3. Click 's' to calculate stage
4. Review the staging result

**Expected result:**
```
🎯 Limb stage determined: 25.3
📊 Confidence: 94.2%
📝 Results saved to: case_studies/hoxa11_pipeline/staging.txt
```

---

### Step 6: Align with Reference

Align the limb with a reference template of the same stage for comparative analysis.

```bash
limblab align case_studies/hoxa11_pipeline/
```

**What happens:**
1. Reference limb of stage 25.3 is loaded
2. Interactive 3D viewer shows both limbs
3. You manually align your limb with the reference
4. Transformation matrix is calculated and saved

**Interactive alignment:**
- **Mouse:** Rotate, pan, zoom
- **'a':** Apply transformation
- **'r':** Reset alignment
- **Close window:** Save transformation

**Alignment benefits:**
- Enables comparative analysis
- Standardizes orientation
- Facilitates multi-sample studies

**Expected result:**
```
✅ Limb aligned with reference
📊 Transformation matrix saved
📝 Pipeline log updated
```

---

### Step 7: Visualize Hoxa11 Expression

Create publication-ready visualizations of the Hoxa11 gene expression.

#### 7.1 3D Isosurface Visualization

```bash
limblab vis isosurfaces case_studies/hoxa11_pipeline HOXA11
```

**What happens:**
1. Interactive isovalue selection for Hoxa11 expression
2. 3D surface rendering with color mapping
3. High-quality visualization with lighting and materials

**Visualization features:**
- **Color mapping:** Expression intensity to color
- **Transparency:** Adjustable opacity
- **Lighting:** Realistic 3D lighting
- **Export:** High-resolution images

**Expected output:**
```
🎨 3D isosurface rendered
📊 Expression range: 0.2 - 0.8
💾 Image saved: case_studies/hoxa11_pipeline/hoxa11_isosurface.png
```

#### 7.2 2D Slab Visualization

```bash
limblab vis slab case_studies/hoxa11_pipeline HOXA11
```

**What happens:**
1. Interactive 2D slicing through the 3D volume
2. Dynamic slab adjustment
3. Real-time expression visualization

**Interactive features:**
- **Mouse wheel:** Adjust slab thickness
- **Mouse drag:** Move slab position
- **Color scale:** Adjust expression range
- **Export:** Save current view

---

## 📊 Results and Analysis

### Expected Outcomes

After completing this tutorial, you should have:

1. **Processed data:**
   - Cleaned DAPI and Hoxa11 volumes
   - 3D surface mesh
   - Staging results
   - Alignment transformation

2. **Visualizations:**
   - 3D isosurface of Hoxa11 expression
   - 2D slab projections
   - Publication-ready images

3. **Analysis insights:**
   - Limb developmental stage
   - Spatial distribution of Hoxa11
   - Expression patterns relative to limb morphology

### Data Files Generated

```
case_studies/hoxa11_pipeline/
├── pipeline.log                    # Processing log
├── HCR11_HOXA11_l1_dapi_488_LH_cleaned.tif    # Cleaned DAPI
├── HCR11_HOXA11_l1_hoxa11_647_LH_cleaned.tif  # Cleaned Hoxa11
├── HCR11_HOXA11_l1_dapi_488_LH_surface.vtk    # 3D surface
├── staging.txt                     # Staging results
├── transformation_matrix.txt       # Alignment data
└── visualizations/                 # Generated images
    ├── hoxa11_isosurface.png
    └── hoxa11_slab.png
```

### Troubleshooting

**Common issues and solutions:**

1. **Volume too large to load:**
   - Use the `--size` parameter to reduce output size
   - Example: `--size 256,256,148`

2. **Poor surface quality:**
   - Adjust isovalues during surface extraction
   - Try different threshold values

3. **Staging fails:**
   - Ensure points are placed along the limb axis
   - Use more points for better accuracy

4. **Alignment issues:**
   - Start with gross alignment, then refine
   - Use the reset function if needed

## 🔬 Scientific Context

### Hoxa11 in Limb Development

Hoxa11 is a homeobox gene that plays a crucial role in:
- **Proximal-distal patterning** of the limb
- **Digit formation** and specification
- **Joint development** and segmentation

### 3D Analysis Advantages

Compared to 2D sections, 3D analysis provides:
- **Complete spatial context** of gene expression
- **Quantitative volume measurements**
- **Better understanding** of expression gradients
- **More accurate** comparative analysis

## 📚 Next Steps

After completing this tutorial, you can:

1. **Compare multiple samples** using the same pipeline
2. **Analyze other genes** in the same limb
3. **Create time series** studies
4. **Export data** for statistical analysis
5. **Generate publication figures** with custom styling

## 🆘 Getting Help

- **Documentation:** Check the user guide for detailed explanations
- **Issues:** Report problems on our GitHub repository
- **Community:** Join our discussion forum
- **Email:** Contact the development team

---

*This tutorial demonstrates the power of LimbLab for 3D gene expression analysis. The same pipeline can be applied to any gene or marker of interest in limb development research.*

