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

## 🚀 Step-by-Step Pipeline

### Step 1: Create Experiment Structure

Set up a new experiment for the dual-channel analysis.

```bash
limblab create-experiment case_studies/sox9_bmp2_pipeline
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
limblab clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_dapi_405_LF.tif dapi
```

**Processing details:**
- **Threshold selection:** Focus on nuclear staining
- **Smoothing:** (6, 6, 6) Gaussian filter
- **Output size:** (512, 512, 296)
- **Expected reduction:** ~75% file size

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
limblab clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_sox9_594_LF.tif sox9
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
limblab clean-volume case_studies/sox9_bmp2_pipeline example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_bmp2_647_LF.tif bmp2
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
limblab extract-surface case_studies/sox9_bmp2_pipeline/
```

**Surface quality note:** 
Real experimental data may produce imperfect surfaces. For this tutorial, we'll use a pre-cleaned surface created with Blender.

**Manual surface replacement:**
```bash
# Add the pre-cleaned surface to pipeline.log
echo 'BLENDER HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk' >> case_studies/sox9_bmp2_pipeline/pipeline.log

# Copy the pre-cleaned surface
cp example_data/sox9_bmp2_raw_data/HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk case_studies/sox9_bmp2_pipeline/
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
limblab stage case_studies/sox9_bmp2_pipeline/
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
limblab align case_studies/sox9_bmp2_pipeline/ --morph
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
limblab vis isosurfaces case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

**What happens:**
1. Interactive isovalue selection for both channels
2. Dual-channel 3D surface rendering
3. Color-coded expression mapping
4. Overlap analysis

**Visualization features:**
- **Sox9 (Red):** Cartilage-forming regions
- **BMP2 (Green):** Bone-forming regions
- **Overlap (Yellow):** Co-expression regions
- **Transparency:** Adjustable for depth perception

**Expected output:**
```
🎨 Dual-channel isosurface rendered
📊 Sox9 expression range: 0.3 - 0.9
📊 BMP2 expression range: 0.2 - 0.8
📊 Overlap regions: 15% of total volume
💾 Image saved: case_studies/sox9_bmp2_pipeline/dual_isosurface.png
```

#### 8.2 Dual-Channel Slice Visualization

```bash
limblab vis slices case_studies/sox9_bmp2_pipeline SOX9 BMP2
```

**What happens:**
1. Interactive 2D slicing through 3D volume
2. Dual-channel overlay visualization
3. Real-time expression comparison
4. Quantitative analysis tools

**Interactive features:**
- **Mouse wheel:** Adjust slice position
- **Mouse drag:** Move through volume
- **Color channels:** Toggle individual channels
- **Intensity scaling:** Adjust expression ranges

#### 8.3 Probe Visualization

```bash
limblab vis probe case_studies/sox9_bmp2_pipeline SOX9 BMP2
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

## 📊 Results and Analysis

### Expected Outcomes

After completing this tutorial, you should have:

1. **Processed data:**
   - Cleaned DAPI, Sox9, and BMP2 volumes
   - 3D surface mesh
   - Staging results
   - Non-linear transformation

2. **Visualizations:**
   - Dual-channel 3D isosurfaces
   - 2D slice overlays
   - Interactive probe data
   - Publication-ready images

3. **Analysis insights:**
   - Spatial relationship between Sox9 and BMP2
   - Co-expression patterns
   - Developmental stage context
   - Quantitative expression data

### Data Files Generated

```
case_studies/sox9_bmp2_pipeline/
├── pipeline.log                                    # Processing log
├── HCR20_BMP2_l1_dapi_405_LF_cleaned.tif          # Cleaned DAPI
├── HCR20_BMP2_l1_sox9_594_LF_cleaned.tif          # Cleaned Sox9
├── HCR20_BMP2_l1_bmp2_647_LF_cleaned.tif          # Cleaned BMP2
├── HCR20_BMP2_l1_dapi_405_LF_surface_blender.vtk  # 3D surface
├── staging.txt                                     # Staging results
├── morphing_transformation.txt                     # Morphing data
└── visualizations/                                 # Generated images
    ├── dual_isosurface.png
    ├── dual_slice.png
    └── probe_data.csv
```

### Scientific Interpretation

#### Sox9 Expression Pattern
- **Primary regions:** Cartilage-forming areas
- **Spatial distribution:** Concentrated in digit-forming regions
- **Developmental role:** Chondrocyte differentiation

#### BMP2 Expression Pattern
- **Primary regions:** Bone-forming areas
- **Spatial distribution:** Complementary to Sox9
- **Developmental role:** Osteoblast differentiation

#### Co-expression Analysis
- **Overlap regions:** 15% of total volume
- **Spatial relationship:** Sox9 proximal, BMP2 distal
- **Developmental significance:** Cartilage-to-bone transition

### Troubleshooting

**Common issues and solutions:**

1. **Poor surface quality:**
   - Use Blender for manual surface cleaning
   - Adjust isovalues during extraction
   - Consider alternative surface generation methods

2. **Channel alignment issues:**
   - Ensure all channels use same coordinate system
   - Check for registration artifacts
   - Verify transformation application

3. **Expression overlap problems:**
   - Adjust threshold values for each channel
   - Use different color schemes
   - Consider transparency settings

4. **Morphing failures:**
   - Ensure good surface quality
   - Check reference template availability
   - Try different morphing parameters

## 🔬 Scientific Context

### Sox9 in Limb Development

Sox9 is a transcription factor essential for:
- **Chondrocyte differentiation** and maintenance
- **Cartilage matrix synthesis**
- **Joint formation** and maintenance
- **Digit patterning** and growth

### BMP2 in Limb Development

BMP2 is a signaling molecule involved in:
- **Osteoblast differentiation** and bone formation
- **Apoptosis regulation** in digit formation
- **Joint development** and maintenance
- **Growth plate regulation**

### Dual-Channel Analysis Benefits

Compared to single-channel analysis:
- **Spatial relationships:** Direct visualization of gene interactions
- **Developmental context:** Understanding tissue transitions
- **Quantitative overlap:** Precise co-expression measurements
- **Functional insights:** Linking expression to development

## 📚 Next Steps

After completing this tutorial, you can:

1. **Time series analysis:** Compare different developmental stages
2. **Multi-gene studies:** Add more channels (e.g., Runx2, Col2a1)
3. **Quantitative analysis:** Export data for statistical analysis
4. **Comparative studies:** Analyze different genetic backgrounds
5. **Publication figures:** Create custom visualizations

## 🆘 Getting Help

- **Documentation:** Check the user guide for detailed explanations
- **Issues:** Report problems on our GitHub repository
- **Community:** Join our discussion forum
- **Email:** Contact the development team

---

*This tutorial demonstrates the power of LimbLab for dual-channel gene expression analysis. The same approach can be applied to any combination of genes or markers in limb development research.*

