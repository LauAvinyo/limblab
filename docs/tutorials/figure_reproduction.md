# Publication-Quality Figure Reproduction Tutorial

Welcome to the comprehensive guide for creating publication-quality figures using LimbLab! This tutorial will teach you how to generate high-resolution, publication-ready visualizations that meet journal standards.

## 🎯 Objective

The goal of this tutorial is to demonstrate how to create publication-quality figures from your 3D limb data. You'll learn advanced visualization techniques, proper image formatting, and best practices for scientific figure creation.

**What you'll learn:**
- High-resolution image generation
- Custom color schemes and styling
- Multi-panel figure creation
- Export formats for different journals
- Figure optimization techniques

## 📁 Prerequisites

Before starting this tutorial, you should have:
- Completed the basic pipeline (volume cleaning, surface extraction, staging, alignment)
- Processed data with at least one gene expression channel
- Basic understanding of the LimbLab workflow

**Required data:**
- Cleaned volume files (.tif format)
- 3D surface mesh (.vtk format)
- Staging and alignment results

## 🚀 Step-by-Step Figure Creation

### Step 1: Prepare Your Data

Ensure your data is properly processed and organized.

```bash
# Check your experiment structure
ls -la case_studies/your_experiment/

# Verify pipeline.log contains all necessary information
cat case_studies/your_experiment/pipeline.log
```

**Expected structure:**
```
case_studies/your_experiment/
├── pipeline.log
├── *_cleaned.tif          # Cleaned volumes
├── *_surface.vtk          # 3D surface
├── staging.txt            # Staging results
└── transformation_matrix.txt  # Alignment data
```

---

### Step 2: Create High-Resolution Isosurface

Generate a publication-quality 3D isosurface visualization.

```bash
limblab vis isosurfaces case_studies/your_experiment GENE_NAME --high-res
```

**Visualization settings:**
- **Resolution:** 300 DPI minimum
- **Color scheme:** Scientific color maps
- **Lighting:** Three-point lighting setup
- **Background:** Clean white or transparent
- **Scale bar:** Include for reference

**Expected output:**
```
🎨 High-resolution isosurface generated
📊 Resolution: 300 DPI
📐 Image size: 2400x1800 pixels
💾 Saved as: case_studies/your_experiment/high_res_isosurface.png
```

---

### Step 3: Generate Multi-Channel Visualization

Create dual or multi-channel visualizations for comparative analysis.

```bash
# Dual-channel visualization
limblab vis isosurfaces case_studies/your_experiment GENE1 GENE2 --high-res

# Multi-channel visualization
limblab vis isosurfaces case_studies/your_experiment GENE1 GENE2 GENE3 --high-res
```

**Color scheme recommendations:**
- **Single channel:** Grayscale or single color
- **Dual channel:** Red-Green or Blue-Red
- **Multi-channel:** Distinct colors (avoid red-green for colorblind accessibility)

**Expected output:**
```
🎨 Multi-channel isosurface generated
📊 Channels: GENE1 (Red), GENE2 (Green)
📊 Overlap regions highlighted
💾 Saved as: case_studies/your_experiment/multi_channel_isosurface.png
```

---

### Step 4: Create 2D Slice Visualizations

Generate high-quality 2D slice images for detailed analysis.

```bash
# Single channel slice
limblab vis slices case_studies/your_experiment GENE_NAME --high-res

# Dual channel slice
limblab vis slices case_studies/your_experiment GENE1 GENE2 --high-res
```

**Slice positioning:**
- **Sagittal:** Proximal-distal view
- **Coronal:** Dorsal-ventral view
- **Transverse:** Anterior-posterior view

**Expected output:**
```
🎨 High-resolution slice generated
📊 Slice position: Sagittal (midline)
📊 Expression range: 0.2 - 0.8
💾 Saved as: case_studies/your_experiment/slice_sagittal.png
```

---

### Step 5: Generate Dynamic Slab Visualization

Create dynamic slab visualizations for depth analysis.

```bash
limblab vis slab case_studies/your_experiment GENE_NAME --high-res
```

**Slab features:**
- **Thickness control:** Adjustable slab depth
- **Position control:** Move through volume
- **Color mapping:** Expression intensity
- **Export options:** Multiple formats

**Expected output:**
```
🎨 Dynamic slab visualization generated
📊 Slab thickness: 50 μm
📊 Position: Mid-volume
💾 Saved as: case_studies/your_experiment/dynamic_slab.png
```

---

### Step 6: Create Probe Analysis Figures

Generate quantitative analysis figures using probe visualization.

```bash
limblab vis probe case_studies/your_experiment GENE1 GENE2 --export-data
```

**Probe analysis:**
- **Point measurements:** Single location data
- **Line profiles:** Expression along paths
- **Volume analysis:** Regional statistics
- **Statistical output:** CSV format

**Expected output:**
```
📊 Probe analysis completed
📈 Data exported: case_studies/your_experiment/probe_data.csv
📊 Statistical summary generated
💾 Saved as: case_studies/your_experiment/probe_analysis.png
```

---

### Step 7: Generate Raycast Visualizations

Create high-quality volume renderings using raycasting.

```bash
limblab vis raycast case_studies/your_experiment GENE_NAME --high-res
```

**Raycast features:**
- **Volume rendering:** Full 3D volume
- **Transfer functions:** Custom opacity mapping
- **Lighting:** Advanced lighting models
- **Depth cues:** Enhanced depth perception

**Expected output:**
```
🎨 Raycast visualization generated
📊 Transfer function: Custom mapping
📊 Lighting: Phong model
💾 Saved as: case_studies/your_experiment/raycast_volume.png
```

---

## 📊 Figure Assembly and Optimization

### Creating Multi-Panel Figures

Combine multiple visualizations into a single publication figure.

**Recommended layout:**
```
┌─────────────┬─────────────┐
│   Panel A   │   Panel B   │
│ (3D Surface)│ (2D Slice)  │
├─────────────┼─────────────┤
│   Panel C   │   Panel D   │
│ (Probe Data)│ (Statistics)│
└─────────────┴─────────────┘
```

**Assembly steps:**
1. **Import images** into vector graphics software (Inkscape, Adobe Illustrator)
2. **Arrange panels** with consistent spacing
3. **Add labels** (A, B, C, D) and scale bars
4. **Include legends** for color schemes
5. **Add text annotations** for key features

### Image Optimization

**Resolution requirements:**
- **Print journals:** 300-600 DPI
- **Online journals:** 150-300 DPI
- **Posters:** 150 DPI minimum
- **Presentations:** 72-150 DPI

**File formats:**
- **Vector graphics:** SVG, PDF (for line art)
- **Raster images:** PNG, TIFF (for photographs)
- **Publication:** EPS, PDF (journal requirements)

---

## 📋 Journal-Specific Guidelines

### Common Journal Requirements

**Nature/Science:**
- **Resolution:** 300 DPI minimum
- **Format:** TIFF or EPS
- **Color space:** RGB or CMYK
- **Size:** 180mm width maximum

**Cell Press:**
- **Resolution:** 300 DPI
- **Format:** TIFF or PDF
- **Color space:** RGB
- **Size:** 180mm width maximum

**PLOS:**
- **Resolution:** 300 DPI
- **Format:** TIFF, PNG, or PDF
- **Color space:** RGB
- **Size:** 190mm width maximum

### Color Accessibility

**Colorblind-friendly palettes:**
- **Viridis:** Blue to yellow
- **Plasma:** Purple to yellow
- **Inferno:** Black to yellow
- **Cividis:** Blue to yellow (optimized for colorblind)

**Avoid combinations:**
- Red and green (protanopia/deuteranopia)
- Blue and yellow (tritanopia)
- Low contrast combinations

---

## 🎨 Advanced Styling Techniques

### Custom Color Schemes

Create custom color schemes for specific applications.

```python
# Example: Custom color scheme for gene expression
import numpy as np
import matplotlib.pyplot as plt

# Create custom colormap
colors = ['#000000', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
custom_cmap = plt.cm.colors.ListedColormap(colors)

# Apply to visualization
limblab.vis.isosurfaces(experiment_path, gene_name, colormap=custom_cmap)
```

### Lighting and Materials

**Three-point lighting setup:**
- **Key light:** Main illumination (45° angle)
- **Fill light:** Soft fill (opposite side)
- **Back light:** Rim lighting (behind subject)

**Material properties:**
- **Diffuse reflection:** Surface color
- **Specular reflection:** Highlight intensity
- **Ambient occlusion:** Shadow depth
- **Transparency:** Alpha channel control

---

## 📊 Data Export and Analysis

### Quantitative Data Export

Export quantitative data for statistical analysis.

```bash
# Export expression data
limblab export-expression case_studies/your_experiment GENE_NAME --format csv

# Export spatial coordinates
limblab export-coordinates case_studies/your_experiment --format xyz

# Export statistics
limblab export-stats case_studies/your_experiment --format json
```

**Export formats:**
- **CSV:** Spreadsheet analysis
- **JSON:** Programmatic access
- **HDF5:** Large datasets
- **MAT:** MATLAB compatibility

### Statistical Analysis

**Common analyses:**
- **Expression quantification:** Mean, median, standard deviation
- **Spatial correlation:** Pearson's correlation coefficient
- **Regional analysis:** ANOVA between regions
- **Time series:** Linear regression analysis

---

## 🔧 Troubleshooting

### Common Issues and Solutions

**1. Low image quality:**
- Increase resolution settings
- Use anti-aliasing
- Check export format

**2. Poor color representation:**
- Use scientific color maps
- Check color space settings
- Verify monitor calibration

**3. Large file sizes:**
- Compress images appropriately
- Use vector formats when possible
- Optimize for intended use

**4. Inconsistent lighting:**
- Use consistent lighting setup
- Save lighting presets
- Apply to all visualizations

### Performance Optimization

**For large datasets:**
- **Downsample** for preview
- **Use GPU acceleration** when available
- **Batch process** multiple visualizations
- **Optimize memory usage**

---

## 📚 Best Practices

### Figure Design Principles

1. **Clarity:** Make the main point obvious
2. **Simplicity:** Remove unnecessary elements
3. **Consistency:** Use consistent styling
4. **Accessibility:** Ensure colorblind-friendly palettes
5. **Reproducibility:** Document all settings

### Workflow Recommendations

1. **Plan ahead:** Sketch your figure layout
2. **Use templates:** Create reusable templates
3. **Version control:** Save multiple versions
4. **Document settings:** Record all parameters
5. **Get feedback:** Review with colleagues

---

## 📖 Example Publications

### Sample Figure Layouts

**Figure 1: Overview**
- Panel A: 3D isosurface (overview)
- Panel B: 2D slice (detail)
- Panel C: Expression profile (quantitative)

**Figure 2: Comparative Analysis**
- Panel A: Control condition
- Panel B: Experimental condition
- Panel C: Overlay comparison
- Panel D: Statistical analysis

**Figure 3: Time Series**
- Panels A-D: Different time points
- Panel E: Quantitative comparison
- Panel F: Statistical summary

---

## 🆘 Getting Help

- **Documentation:** Check the user guide for detailed explanations
- **Examples:** Review sample figures in the repository
- **Community:** Join our discussion forum
- **Support:** Contact the development team

---

*This tutorial provides the foundation for creating publication-quality figures with LimbLab. Remember that good scientific visualization is both an art and a science - practice and experimentation will help you develop your own style while maintaining scientific rigor.*
