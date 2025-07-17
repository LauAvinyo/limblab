# Hoxa11 Gene Expression Analysis Tutorial

Welcome to the comprehensive guide for analyzing Hoxa11 gene expression using LimbLab! This tutorial will walk you through the complete pipeline for processing and visualizing 3D limb data with Hoxa11 expression.

## Objective

The goal of this tutorial is to analyze Hoxa11 gene expression in mouse limb development using Hybridization Chain Reaction (HCR) data. Hoxa11 is a crucial gene involved in limb patterning and development. By analyzing it in 3D, we can gain insights that might be missed in traditional 2D projections.

**What you'll learn:**

- Setting up experiments in LimbLab
- Processing raw volume data
- Extracting 3D surfaces
- Staging limbs automatically
- Aligning with reference templates
- Creating publication-ready visualizations

## Data Overview

**Dataset:** Hoxa11 HCR expression [data](https://www.ebi.ac.uk/biostudies/BioImages/studies/S-BIAD1926?query=HCR11%20)  
**Location:** `example_data/hoxa11_raw_data/`  
**Channels:** 

- DAPI (nuclear staining)
- Hoxa11 (gene expression)

**Files:**

- `HCR11_HOXA11_l1_dapi_488_LH.tif` - DAPI channel
- `HCR11_HOXA11_l1_hoxa11_647_LH.tif` - Hoxa11 channel

### Download the data

On your terminal (MacOS, WSL or Linux), create a new folder.

```bash
mkdir example_data
mkdir example_data/hoxa11_raw_data
```
Then, you go to: [data bioimage archive](https://www.ebi.ac.uk/biostudies/BioImages/studies/S-BIAD1926?query=HCR11%20)

From here you can download the needed files and locate them to the folder `example_data/hoxa11_raw_data/` 

You should be able to do 
```
ls example_data\hoxa11_raw_data
```

And see, or something (very) similar
```
HCR11_HOXA11_l1_cntl_488_LH.tif
HCR11_HOXA11_l1_hoxa11_647_LH.tif
HCR11_HOXA11_l1_hoxa13_546_LH.tif
HCR11_HOXA11_l1_sox9_594_LH.tif
````

## Step-by-Step Pipeline

### Step 1: Create Experiment Structure

First, we need to create a new experiment folder to keep our raw data safe and organized.

```bash
mkdir case_studies
limb create-experiment case_studies/hoxa11_pipeline
```

**What happens:** LimbLab creates a new directory structure and initializes a `pipeline.log` file to track all processing steps.

**Interactive prompts:**

- **Limb side:** Select `L` (Left)
- **Limb position:** Select `H` (Hindlimb) 
- **Microscope spacing:** Use default `0.65 0.65 2.0`

**Your `pipeline.log` should contain:**
(`cat case_studies/hoxa11_pipeline/pipeline.log`)
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
limb clean-volume case_studies/hoxa11_pipeline example_data/hoxa11_raw_data/HCR11_HOXA11_l1_cntl_488_LH.tif  DAPI
```


**What happens:** 

1. LimbLab loads the raw DAPI volume
2. An interactive plotter appears showing the volume histogram
3. You select threshold values to remove background noise. Note that the goal is to select the surface. As 
4. The volume is processed with smoothing and filtering

**Interactive steps:**

1. **Threshold selection:** Click to set bottom and top isovalues
2. **Preview:** Review the cleaned volume
3. **Confirm:** Accept the processing parameters
4. **Wait...**

**Processing details:**

- Gaussian smoothing: (6, 6, 6)
- Frequency cutoff: 0.05
- Output size: (512, 512, 296)


<img src="../../assets/image102.png" alt="Clean Dapi Channel 1" width="300"/>
<img src="../../assets/image103.png" alt="Clean Dapi Channel 2" width="300"/>

---

### Step 3: Clean Hoxa11 Volume

Now we process the Hoxa11 gene expression channel using the same cleaning pipeline.

```bash
limb clean-volume case_studies/hoxa11_pipeline example_data/hoxa11_raw_data/HCR11_HOXA11_l1_hoxa11_647_LH.tif HOXA11
```



**What happens:** Same cleaning process as DAPI, but optimized for gene expression data.

**Key differences:**

- Different threshold values
- Same smoothing and filtering parameters
- Maintains spatial relationship with DAPI channel


<img src="../../assets/image105.png" alt="Clean Hoxa11 Channel 1" width="300"/>
<img src="../../assets/image106.png" alt="Clean Hoxa11 Channel 2" width="300"/>
---

### Step 4: Extract 3D Surface

We create a 3D surface mesh from the DAPI volume for further analysis and visualization.

```bash
limb extract-surface case_studies/hoxa11_pipeline/
```

**What happens:**

1. LimbLab loads the cleaned DAPI volume
2. Interactive isovalue selection for surface extraction - once you are happy with the value click `q`
3. Surface mesh generation using marching cubes algorithm
4. Mesh decimation for performance optimization

**Interactive steps:**
**Isovalue selection:** Choose the intensity threshold for surface

**Technical details:**

- Algorithm: Marching cubes
- Decimation: 0.5% of original points
- Format: VTK file

<img src="../../assets/image107.png" alt="Surface" width="400"/>

---

### Step 5: Stage the Limb

Determine the developmental stage of the limb using our automated staging algorithm.

```bash
limb stage case_studies/hoxa11_pipeline/
```

**What happens:**

1. Interactive 3D viewer opens with the limb surface
2. You place points along the limb's long axis
3. A spline is fitted through the points
4. The algorithm calculates the developmental stage
5. Review the staging result

**Interactive controls:**

- **Left click:** Add point
- **Right click:** Remove point  
- **'c':** Clear all points
- **'s':** Stage the limb
- **'r':** Reset camera
- **'q':** Quit

<img src="../../assets/image108.png" alt="Surface" width="800"/>

---

### Step 6: Align with Reference

Align the limb with a reference template of the same stage for comparative analysis.

```bash
limb align case_studies/hoxa11_pipeline/
```

**What happens:**

1. Reference limb of stage loaded
2. Interactive 3D viewer shows both limbs
3. You manually align your limb with the reference. TIP: use Ctr/shift/alt for better rotation!
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

<img src="../../assets/image109.png" alt="Surface" width="400"/>

---

### Step 7: Visualize Hoxa11 Expression

Create publication-ready visualizations of the Hoxa11 gene expression.

#### 7.1 3D Isosurface Visualization

```bash
limb vis isosurfaces case_studies/hoxa11_pipeline HOXA11
```

**What happens:**
1. Interactive isovalue selection for Hoxa11 expression (if not done previously!)
2. 3D surface rendering with color mapping
3. High-quality visualization with lighting and materials

**Visualization features:**
- **Transparency:** Adjustable opacity (CLick to the isosurface and use the right/left arrow keys)
- **Lighting:** Realistic 3D lighting
- **Export:** Screenshoot your view with `Shift + s`

<img src="../../assets/image110.png" alt="Surface" width="300"/>
<img src="../../assets/image111.png" alt="Surface" width="300"/>
---

## Results and Analysis

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


### Troubleshooting

**Common issues and solutions:**

1. **Volume too large to load:**
      - Use the `--size` parameter to reduce output size
      - Example: `--size 256,256,148`

2. **Poor surface quality:**
      - Adjust isovalues during surface extraction
      - Try different threshold values

3. **Staging fails:**
      - Ensure points are placed along the limb AER
      - Use more points for better accuracy

4. **Alignment issues:**
      - Start with gross alignment, then refine
      - Use the reset function if needed

## Scientific Context

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



---

*This tutorial demonstrates the power of LimbLab for 3D gene expression analysis. The same pipeline can be applied to any gene or marker of interest in limb development research.*

