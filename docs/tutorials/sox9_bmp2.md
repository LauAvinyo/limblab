# Sox9 and BMP2 Dual-Channel Analysis Tutorial

Welcome to the comprehensive guide for analyzing Sox9 and BMP2 gene expression using LimbLab! This tutorial focuses on dual-channel analysis, which is crucial for understanding gene interactions and spatial relationships in limb development. For more details on basic analysis look the tutorial on Hoxa11!

## Objective

The goal of this tutorial is to analyze the spatial relationship between Sox9 and BMP2 gene expression in mouse limb development. Sox9 is essential for cartilage formation, while BMP2 regulates bone development. Understanding their 3D co-expression patterns provides insights into the molecular mechanisms of limb development.

**What you'll learn:**
- Dual-channel volume processing
- Comparative gene expression analysis
- Spatial relationship mapping
- Multi-channel visualization techniques
- Advanced alignment and morphing

## Data Overview

**Dataset:** Sox9 and BMP2 HCR expression data  
**Location:** `example_data/sox9_bmp2_raw_data/`  
**Channels:** 
- DAPI (nuclear staining)
- Sox9 (cartilage marker)
- BMP2 (bone morphogenetic protein)

**Files:**
- `HCR20_BMP2_l1_dapi_405_LF.tif` - DAPI channel
- `HCR20_BMP2_l1_sox9_594_LF.tif` - Sox9 channel
- `HCR20_BMP2_l1_bmp2_647_LF.tif` - BMP2 channel

### Download the data

On your terminal (MacOS, WSL or Linux), create a new folder.

```bash
mkdir example_data
mkdir example_data/sox9_bmp2_raw_data
```
Then, you go to: [data bioimage archive](https://www.ebi.ac.uk/biostudies/BioImages/studies/S-BIAD1925?query=HCR20%20) 
From here you can download the needed files and locate them to the folder `example_data/sox9_bmp2_raw_data/` 

You should be able to do 
```
ls example_data\sox9_bmp2_raw_data
```

And see, or something (very) similar
```
HCR20_BMP2_l1_dapi_405_LF.tif
HCR20_BMP2_l1_sox9_594_LF.tif
HCR20_BMP2_l1_bmp2_647_LF.tif
```

## Step-by-Step Pipeline

### Step 1: Create Experiment Structure

Set up a new experiment for the dual-channel analysis.

```bash
limb create-experiment case_studies/sox9_bmp2_pipeline
```

**Interactive prompts:**

- **Limb side:** Select `L` (Left)
- **Limb position:** Select `F` (Forelimb)
- **Microscope spacing:** Use default `0.65 0.65 2.0`

**Your `pipeline.log` should contain:**
(`cat case_studies/sox9_bmp2_pipeline/pipeline.log`)
```txt
BASE ./case_studies/sox9_bmp2_pipeline
SIDE L
POSITION F
SPACING 0.65 0.65 2.0
```

---

### Step 2: Clean DAPI Volume

Process the structural reference channel first.

```bash
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_dapi_405_LF.tif dapi
```

**Processing details:**

- **Threshold selection:** Focus on nuclear staining
- **Smoothing:** (6, 6, 6) Gaussian filter
- **Output size:** (512, 512, 296)

<img src="../../assets/image112.png" alt="Clean Dapi Channel 1" width="500"/>

---

### Step 3: Clean Sox9 Volume

Process the Sox9 cartilage marker channel.

```bash
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_sox9_594_LF.tif SOX9
```

**Key considerations for Sox9:**

- **Expression pattern:** Cartilage-forming regions
- **Spatial distribution:** Concentrated in digit-forming areas

<img src="../../assets/image113.png" alt="Clean Sox9 Channel 1" width="500"/>

---

### Step 4: Clean BMP2 Volume

Process the BMP2 bone morphogenetic protein channel.

```bash
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_bmp2_647_LF.tif BMP2
```

**Key considerations for BMP2:**

- **Expression pattern:** Bone-forming regions
- **Relationship to Sox9:** Often complementary expression

<img src="../../assets/image114.png" alt="Clean BMP2 Channel 1" width="500"/>


---

### Step 5: Extract 3D Surface

Create a surface mesh from the DAPI volume for analysis.

```bash
limb extract-surface case_studies/sox9_bmp2_pipeline/
```

<img src="../../assets/image115.png" alt="Clean BMP2 Channel 1" width="500"/>


**Surface quality note:** 

Real experimental data may produce imperfect surfaces. 

*OPTIONALLY*, you can clean the surface created with Blender. Then, LimbLab will use it by default.
Note use vtk in blender you just need 

**Manual surface replacement:**

```bash
# Add the pre-cleaned surface to pipeline.log
echo 'BLENDER HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk' >> case_studies/sox9_bmp2_pipeline/pipeline.log

# Copy the pre-cleaned surface
cp ${your_path}/HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk case_studies/sox9_bmp2_pipeline/
```

<img src="../../assets/image117.png" alt="Alignment" width="800"/>

---

### Step 6: Stage the Limb

Determine the developmental stage for proper reference alignment.

```bash
limb stage case_studies/sox9_bmp2_pipeline/
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

<img src="../../assets/image116.png" alt="Staging" width="800"/>

---

### Step 7: Align with Reference (Morphing)

Use non-linear morphing for precise alignment with the reference template.

```bash
limb align case_studies/sox9_bmp2_pipeline/ --morph
```

**Why morphing for dual-channel analysis:**

- **Better alignment:** Non-linear transformation captures complex morphology
- **Preserves relationships:** Maintains spatial relationships between channels
- **Higher accuracy:** Essential for comparative analysis

**Morphing process:**

1. Reference template of stage 24.7 is loaded
2. Non-linear registration is performed
3. Transformation is applied to all channels
4. Results are saved for visualization

<img src="../../assets/image118.png" alt="Alignment" width="800"/>

---

### Step 8: Dual-Channel Visualization

Create comprehensive visualizations of both gene expression patterns.

#### 8.1 Dual-Channel Isosurface Visualization



```bash
limb vis isosurfaces case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

<img src="../../assets/image119.png" alt="Dual Isosurface" width="800"/>



```bash
limb vis slices case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

**What happens:**

1. Interactive 2D slicing through 3D volume


#### 8.2 Probe Visualization

```bash
limb vis probe case_studies/sox9_bmp2_pipeline  BMP2 SOX9
```

**What happens:**

1. Interactive probe placement
2. Real-time expression measurement
3. Multi-channel data extraction


**Probe features:**

- **Line probes:** Linear expression profiles
- **Volume probes:** Regional analysis


<img src="../../assets/image120.png" alt="Dual Isosurface" width="500"/>

---

## Results and Analysis

### Expected Outcomes

After completing this tutorial, you should have:

1.  **Processed data:**
    -   Cleaned DAPI, Sox9, and BMP2 volumes
    -   3D surface mesh
    -   Staging results
    -   Non-linear transformation

2.  **Visualizations:**
    -   Dual-channel 3D isosurfaces
    -   2D slice overlays
    -   Interactive probe data
    -   Publication-ready images

3.  **Analysis insights:**
    -   Spatial relationship between Sox9 and BMP2
    -   Co-expression patterns
    -   Developmental stage context

### Troubleshooting

**Common issues and solutions:**

1.  **Volume too large to load:**
    -   Use the `--size` parameter to reduce output size
    -   Example: `--size 256,256,148`

2.  **Poor surface quality:**
    -   Adjust isovalues during surface extraction
    -   Try different threshold values

3.  **Staging fails:**
    -   Ensure points are placed along the limb AER
    -   Use more points for better accuracy

4.  **Alignment issues:**
    -   The non-linear morphing is a powerful but complex algorithm. Results may vary depending on data quality.

---
*This tutorial demonstrates the power of LimbLab for dual-channel gene expression analysis. The same approach can be applied to any combination of genes or markers in limb development research.*

