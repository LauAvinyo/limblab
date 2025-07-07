# Volume Processing Guide

This guide provides comprehensive information about the volume processing capabilities in LimbLab. The `clean_volume` function is the foundation of the LimbLab pipeline, transforming raw imaging data into analysis-ready volumes.

## 🎯 Overview

Volume processing in LimbLab involves several key steps designed to:
- **Remove noise** and artifacts from raw data
- **Standardize** volume dimensions and spacing
- **Optimize** data for downstream analysis
- **Preserve** biological signal while reducing file size

## 🔧 The `clean_volume` Function

### Basic Usage

```bash
limblab clean-volume EXPERIMENT_PATH VOLUME_PATH CHANNEL_NAME
```

**Parameters:**
- `EXPERIMENT_PATH`: Path to your experiment directory
- `VOLUME_PATH`: Path to raw volume file (.tif format)
- `CHANNEL_NAME`: Channel identifier (e.g., DAPI, GFP, RFP)

### Advanced Usage with Custom Parameters

```bash
limblab clean-volume EXPERIMENT_PATH VOLUME_PATH CHANNEL_NAME \
  --sigma 8,8,8 \
  --cutoff 0.03 \
  --size 1024,1024,296
```

## 📊 Processing Pipeline

### Step 1: Data Loading and Validation

**What happens:**
1. **File validation:** Check format and integrity
2. **Metadata extraction:** Read voxel spacing and dimensions
3. **Memory allocation:** Prepare for processing
4. **Pipeline log update:** Record processing parameters

**Expected output:**
```
📊 Loading volume: raw_data.tif
🎯 Channel: DAPI
📏 Voxel spacing: 0.65 0.65 2.0 μm
📐 Volume dimensions: 1024x1024x296
💾 Memory usage: 1.2GB
```

### Step 2: Interactive Thresholding

**Purpose:** Remove background noise and select signal range

**Interactive workflow:**
1. **Histogram display:** Shows intensity distribution
2. **Threshold selection:** Click to set bottom and top values
3. **Real-time preview:** See the effect of your choices
4. **Confirmation:** Accept or adjust parameters

**Thresholding guidelines:**
- **Bottom threshold:** Remove background noise
- **Top threshold:** Remove saturated pixels
- **Signal preservation:** Ensure biological signal remains
- **Consistency:** Use similar values across similar channels

### Step 3: Volume Clipping and Resizing

**Processing steps:**
1. **Threshold application:** Clip values outside selected range
2. **Volume resizing:** Resize to standard dimensions
3. **Memory optimization:** Reduce memory footprint
4. **Coordinate system:** Maintain spatial relationships

**Default parameters:**
- **Output size:** (512, 512, 296) voxels
- **Data type:** 16-bit unsigned integer
- **Compression:** LZW compression for TIFF files

### Step 4: Noise Reduction

**Gaussian smoothing:**
- **Purpose:** Reduce high-frequency noise
- **Default parameters:** (6, 6, 6) sigma values
- **Effect:** Smooths volume while preserving structure
- **Customization:** Adjust for different data types

**Frequency filtering:**
- **Purpose:** Remove periodic artifacts
- **Default cutoff:** 0.05 (low-pass filter)
- **Effect:** Removes high-frequency components
- **Application:** Particularly useful for confocal data

### Step 5: Spatial Standardization

**Mirroring (for left limbs):**
- **Purpose:** Standardize orientation
- **Application:** Left side limbs are mirrored
- **Effect:** Enables direct comparison with reference templates
- **Preservation:** Maintains spatial relationships

**Coordinate system:**
- **Origin:** Standardized reference point
- **Axes:** Consistent orientation across samples
- **Spacing:** Preserved voxel dimensions
- **Alignment:** Ready for template matching

## 🎛️ Custom Parameters

### Gaussian Smoothing (`--sigma`)

**Format:** `x,y,z` values for each dimension

**Examples:**
```bash
# Default smoothing
--sigma 6,6,6

# Increased smoothing (more noise reduction)
--sigma 8,8,8

# Anisotropic smoothing (different for each axis)
--sigma 4,4,8

# Minimal smoothing (preserve detail)
--sigma 2,2,2
```

**When to adjust:**
- **High noise:** Increase sigma values
- **Fine detail:** Decrease sigma values
- **Anisotropic data:** Use different values per axis
- **Confocal data:** Often benefit from higher smoothing

### Frequency Cutoff (`--cutoff`)

**Range:** 0.01 to 0.5 (lower = more aggressive filtering)

**Examples:**
```bash
# Default filtering
--cutoff 0.05

# Aggressive filtering (remove more artifacts)
--cutoff 0.02

# Minimal filtering (preserve more detail)
--cutoff 0.1

# No filtering
--cutoff 0.5
```

**When to adjust:**
- **Periodic artifacts:** Lower cutoff values
- **High-quality data:** Higher cutoff values
- **Confocal data:** Often benefit from lower cutoff
- **Light sheet data:** May need higher cutoff

### Output Size (`--size`)

**Format:** `x,y,z` dimensions in voxels

**Examples:**
```bash
# Default size (balanced)
--size 512,512,296

# High resolution (more detail)
--size 1024,1024,592

# Low resolution (faster processing)
--size 256,256,148

# Custom aspect ratio
--size 768,512,296
```

**When to adjust:**
- **Large datasets:** Reduce size for memory constraints
- **High detail needed:** Increase size
- **Batch processing:** Use consistent sizes
- **Publication figures:** Higher resolution

## 📈 Performance Optimization

### Memory Management

**Memory requirements:**
- **Raw volume:** 2-4GB per channel
- **Processing:** 4-8GB peak usage
- **Output:** 200-500MB per channel
- **Total:** 8-16GB recommended

**Optimization strategies:**
```bash
# Process smaller volumes
--size 256,256,148

# Use lower precision
--dtype uint8

# Process in batches
# (script multiple commands)
```

### Processing Speed

**Typical processing times:**
- **Small volumes (256³):** 30-60 seconds
- **Medium volumes (512³):** 2-5 minutes
- **Large volumes (1024³):** 10-20 minutes
- **Very large volumes (2048³):** 30-60 minutes

**Speed optimization:**
- **SSD storage:** Faster I/O operations
- **Sufficient RAM:** Reduce swapping
- **GPU acceleration:** Available for some operations
- **Batch processing:** Parallel execution

## 🔍 Quality Control

### Visual Inspection

**What to check:**
1. **Signal preservation:** Biological features visible
2. **Noise reduction:** Background is clean
3. **Artifact removal:** No periodic patterns
4. **Edge preservation:** Sharp boundaries maintained
5. **Contrast:** Good dynamic range

### Quantitative Metrics

**File size reduction:**
- **Typical reduction:** 70-90%
- **Acceptable range:** 50-95%
- **Warning signs:** <50% or >95% reduction

**Signal-to-noise ratio:**
- **Calculate:** Mean signal / Standard deviation of background
- **Target:** >3:1 for analysis
- **Minimum:** >2:1 for visualization

### Common Issues and Solutions

#### Issue: Too Much Noise
**Symptoms:** Grainy appearance, poor contrast
**Solutions:**
```bash
# Increase smoothing
--sigma 8,8,8

# Lower frequency cutoff
--cutoff 0.02

# Check raw data quality
```

#### Issue: Loss of Detail
**Symptoms:** Blurry features, missing structures
**Solutions:**
```bash
# Reduce smoothing
--sigma 4,4,4

# Increase output size
--size 1024,1024,592

# Adjust thresholds
```

#### Issue: Large File Sizes
**Symptoms:** Slow processing, memory issues
**Solutions:**
```bash
# Reduce output size
--size 256,256,148

# Use compression
--compress lzw

# Process in smaller chunks
```

#### Issue: Poor Thresholding
**Symptoms:** Missing signal or too much background
**Solutions:**
- **Re-run with different thresholds**
- **Check raw data histogram**
- **Verify channel selection**
- **Consider data quality**

## 📊 Output Files

### Generated Files

```
experiment/
├── pipeline.log                    # Processing log
├── dapi_cleaned.tif               # Cleaned volume
├── dapi_cleaned_metadata.json     # Processing metadata
└── dapi_cleaned_histogram.png     # Intensity histogram
```

### Pipeline Log Entry

```txt
DAPI ./dapi_cleaned.tif
DAPI_THRESHOLD 120 200
DAPI_SIGMA 6 6 6
DAPI_CUTOFF 0.05
DAPI_SIZE 512 512 296
```

### Metadata File

```json
{
  "channel": "DAPI",
  "original_file": "raw_data.tif",
  "processing_date": "2024-01-15T10:30:00",
  "parameters": {
    "sigma": [6, 6, 6],
    "cutoff": 0.05,
    "size": [512, 512, 296],
    "thresholds": [120, 200]
  },
  "statistics": {
    "original_size_mb": 1200,
    "processed_size_mb": 240,
    "reduction_percent": 80,
    "signal_to_noise": 4.2
  }
}
```

## 🔬 Scientific Applications

### Different Channel Types

#### DAPI (Nuclear Staining)
**Characteristics:** High contrast, uniform distribution
**Recommended parameters:**
```bash
--sigma 6,6,6
--cutoff 0.05
--size 512,512,296
```

#### Gene Expression (HCR, FISH)
**Characteristics:** Variable intensity, specific patterns
**Recommended parameters:**
```bash
--sigma 4,4,4
--cutoff 0.03
--size 1024,1024,592
```

#### Immunofluorescence
**Characteristics:** Variable background, specific staining
**Recommended parameters:**
```bash
--sigma 8,8,8
--cutoff 0.02
--size 512,512,296
```

### Data Quality Considerations

#### High-Quality Data
- **Good signal-to-noise ratio**
- **Uniform illumination**
- **Minimal artifacts**
- **Consistent staining**

#### Challenging Data
- **Low signal intensity**
- **High background**
- **Motion artifacts**
- **Inconsistent staining**

## 📚 Best Practices

### Workflow Recommendations

1. **Start with defaults:** Use standard parameters first
2. **Inspect results:** Always check processed volumes
3. **Document changes:** Record custom parameters
4. **Validate quality:** Ensure biological features preserved
5. **Consistency:** Use same parameters for similar data

### Parameter Selection

1. **Assess data quality:** Check raw data first
2. **Choose smoothing:** Balance noise reduction vs. detail
3. **Set thresholds:** Preserve biological signal
4. **Optimize size:** Balance detail vs. performance
5. **Validate results:** Check processed output

### Quality Assurance

1. **Visual inspection:** Check processed volumes
2. **Quantitative metrics:** Calculate signal-to-noise
3. **Comparison:** Compare with raw data
4. **Documentation:** Record all parameters
5. **Reproducibility:** Use version control

---

## 🆘 Troubleshooting

### Common Error Messages

**"Volume too large to load"**
```bash
# Reduce output size
--size 256,256,148

# Check available memory
# Close other applications
```

**"Invalid threshold values"**
```bash
# Check data range
# Use automatic thresholding
# Verify channel selection
```

**"Processing failed"**
```bash
# Check file permissions
# Verify file format
# Ensure sufficient disk space
```

### Getting Help

- **Documentation:** Check this guide for detailed explanations
- **Examples:** Review sample data and workflows
- **Community:** Ask questions on GitHub Discussions
- **Issues:** Report bugs on GitHub Issues

---

*Volume processing is the foundation of the LimbLab pipeline. Proper processing ensures high-quality results in all downstream analyses. Take time to understand your data and choose appropriate parameters for your specific application.*