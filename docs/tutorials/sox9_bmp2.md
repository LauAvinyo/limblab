# Sox9 and BMP2 Dual-Channel Analysis Tutorial

Welcome to the comprehensive guide for analyzing Sox9 and BMP2 gene expression using LimbLab! This tutorial focuses on dual-channel analysis, which is crucial for understanding gene interactions and spatial relationships in limb development.

## 🎯 Objective

The goal of this tutorial is to analyze the spatial relationship between Sox9 and BMP2 gene expression in mouse limb development. Sox9 is essential for cartilage formation, while BMP2 regulates bone development. Understanding their 3D co-expression patterns provides insights into the molecular mechanisms of limb development.

**What you'll learn:**
- Dual-channel volume processing
- Comparative gene expression analysis
- Spatial relationship mapping
- Multi-channel visualization techniques
- Advanced alignment and morphing

## 📁 Data Overview

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

```bash
mkdir example_data
mkdir example_data/sox9_bmp2_raw_data
```
Then, you go to: XX 
From here you can download the needed files and locate them to the folder `example_data/sox9_bmp2_raw_data/` 


## 🚀 Step-by-Step Pipeline

### Step 1: Create Experiment Structure

Set up a new experiment for the dual-channel analysis.

```bash
limb create-experiment case_studies/sox9_bmp2_pipeline
```

**Interactive prompts:**
- **Limb side:** Select `L` (Left)
- **Limb position:** Select `F` (Forelimb)
- **Microscope spacing:** Use default `0.65 0.65 2.0`

**Expected output:**
```
✅ Experiment created: case_studies/sox9_bmp2_pipeline
📝 Pipeline log initialized
```

**Your `pipeline.log` should contain:**
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

**Expected result:**
```
✅ DAPI volume cleaned and saved
📊 Volume size: 180MB (from 720MB)
📝 Pipeline log updated
```

---

### Step 3: Clean Sox9 Volume

Process the Sox9 cartilage marker channel.

```bash
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_sox9_594_LF.tif sox9
```

**Key considerations for Sox9:**
- **Expression pattern:** Cartilage-forming regions
- **Threshold values:** Typically higher than DAPI
- **Spatial distribution:** Concentrated in digit-forming areas

**Expected result:**
```
✅ Sox9 volume cleaned and saved
📊 Expression preserved in cartilage regions
📝 Pipeline log updated
```

---

### Step 4: Clean BMP2 Volume

Process the BMP2 bone morphogenetic protein channel.

```bash
limb clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_bmp2_647_LF.tif bmp2
```

**Key considerations for BMP2:**
- **Expression pattern:** Bone-forming regions
- **Relationship to Sox9:** Often complementary expression
- **Threshold selection:** Balance signal and background

**Expected result:**
```
✅ BMP2 volume cleaned and saved
📊 Expression preserved in bone-forming regions
📝 Pipeline log updated
```

---

### Step 5: Extract 3D Surface

Create a surface mesh from the DAPI volume for analysis.

```bash
limb extract-surface case_studies/sox9_bmp2_pipeline/
```

**Surface quality note:** 
Real experimental data may produce imperfect surfaces. 

OPTIONALLY, you can clean the surface created with Blender. Then, LimbLab will use it by default.
Note use vtk in blender you just need 

**Manual surface replacement:**
```bash
# Add the pre-cleaned surface to pipeline.log
echo 'BLENDER HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk' >> case_studies/sox9_bmp2_pipeline/pipeline.log

# Copy the pre-cleaned surface
cp ${your_path}/HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk case_studies/sox9_bmp2_pipeline/
```

**Expected result:**
```
✅ Surface mesh loaded
📊 Mesh: 12,845 vertices, 25,690 faces
💾 Using pre-cleaned Blender surface
```

---

### Step 6: Stage the Limb

Determine the developmental stage for proper reference alignment.

```bash
limb stage case_studies/sox9_bmp2_pipeline/
```

**Staging process:**
1. Place points along the proximal-distal axis
2. Focus on digit-forming regions
3. Ensure good point distribution
4. Calculate stage automatically

**Expected result:**
```
🎯 Limb stage determined: 24.7
📊 Confidence: 91.8%
📝 Results saved to: case_studies/sox9_bmp2_pipeline/staging.txt
```

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

**Expected result:**
```
✅ Non-linear morphing completed
📊 Transformation applied to all channels
📝 Pipeline log updated
```

---

### Step 8: Dual-Channel Visualization

Create comprehensive visualizations of both gene expression patterns.

#### 8.1 Dual-Channel Isosurface Visualization

```bash
limb vis isosurfaces case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

**What happens:**
1. Interactive isovalue selection for both channels
2. Dual-channel 3D surface rendering
3. Color-coded expression mapping


#### 8.2 Dual-Channel Slice Visualization

```bash
limb vis slices case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

**What happens:**
1. Interactive 2D slicing through 3D volume
2. Dual-channel overlay visualization
3. Real-time expression comparison

**Interactive features:**
- **Mouse wheel:** Adjust slice position
- **Mouse drag:** Move through volume

#### 8.3 Probe Visualization

```bash
limb vis probe case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

**What happens:**
1. Interactive probe placement
2. Real-time expression measurement
3. Multi-channel data extraction
4. Statistical analysis

**Probe features:**
- **Point probes:** Single-point measurements
- **Line probes:** Linear expression profiles
- **Volume probes:** Regional analysis
- **Export data:** CSV format for further analysis

---

### Data Files Generated

```
case_studies/sox9_bmp2_pipeline/
├── pipeline.log                                    # Processing log
├── HCR20_BMP2_l1_dapi_405_LF_cleaned.tif          # Cleaned DAPI
├── HCR20_BMP2_l1_sox9_594_LF_cleaned.tif          # Cleaned Sox9
├── HCR20_BMP2_l1_bmp2_647_LF_cleaned.tif          # Cleaned BMP2
├── HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk  # 3D surface
├── staging.txt                                     # Staging results
```


*This tutorial demonstrates the power of LimbLab for dual-channel gene expression analysis. The same approach can be applied to any combination of genes or markers in limb development research.*

