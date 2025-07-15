<!-- ![Alt text](assets/logo.png "LimbLab") -->
<div style="text-align: center;">
  <img src="assets/header.png" alt="LimbLab" height="400">
  <p><strong>Work fast, code less.</strong> Analyze your 3D limb data with ease. Aesthetic out of the box.</p>
</div>

---

## 🚀 Quick Start

Get started with LimbLab in minutes:

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

**Need help?** Check out our [tutorials](tutorials/) or [user guide](userGuide/).

---

## Documentation Overview

### Docs
- **[Quick Start Tutorial](tutorials/cli.md)** - Detailed description of the Command line

### Tutorials
- **[Hoxa11 Analysis](tutorials/hoxa11.md)** - Complete single-channel gene expression analysis
- **[Sox9-BMP2 Dual Analysis](tutorials/sox9_bmp2.md)** - Multi-channel comparative analysis

---

## What is LimbLab?

LimbLab is a comprehensive library for processing and analyzing 3D limb development data. Designed specifically for the scientific community working with mouse limb models, it provides a complete pipeline from raw data to publication-ready visualizations.

### Key Features
**🔬 Limb-Specific Tools**

- Semi automate limb staging using 3D morphology

- Limb 3D Reference alignment for comparative analysis

- Specialized algorithms for limb development data


**🎨 Aesthetic Out-of-the-Box** Publication-ready visualizations

**⚙️ Customizable** Built on Vedo for extensibility

**🔬 Trusted by Research** Active use in research laboratories

---

## Complete Analysis Pipeline

LimbLab provides a complete pipeline for 3D limb data analysis:

### 1. **Data Preparation**
```bash
# Create experiment structure
limb create-experiment my_study

# Process raw volumes
limb clean-volume my_study dapi.tif DAPI
limb clean-volume my_study gene.tif GENE
```

### 2. **3D Analysis**
```bash
# Extract surface mesh
limb extract-surface my_study --auto

# Determine developmental stage
limb stage my_study

# Align with reference
limb align my_study
```

### 3. **Visualization**
```bash
# Create 3D visualizations
limb vis isosurfaces my_study GENE
limb vis slices my_study GENE
limb vis raycast my_study GENE
```

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python:** 3.8 or higher
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 10GB free space
- **GPU:** Optional (CUDA support for acceleration)

### Recommended Setup
- **OS:** Latest stable release
- **Python:** 3.9 or 3.10
- **RAM:** 32GB or more
- **Storage:** SSD with 50GB+ free space
- **GPU:** NVIDIA GTX 1060 or better (for acceleration)

---

## Installation

### Quick Install

```bash
pip install limb
```

---

## License & Citation

### License
LimbLab is released under the [MIT License](LICENSE), allowing free use in both academic and commercial applications.

### Citation
If you use LimbLab in your research, please cite:

```bibtex
@software{limblab2024,
  title={LimbLab: A comprehensive library for 3D limb development analysis},
  author={Vinyo, Laura and Contributors},
  year={2024},
  url={https://github.com/lauavinyo/limb}
}
```

---

---

<div style="text-align: center; margin-top: 2rem;">
  <p><em>LimbLab - Empowering 3D limb development research</em></p>
  <p>Made with ❤️ by the Sharpe Lab</p>
</div>
