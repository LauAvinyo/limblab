# Getting Help with LimbLab

Need assistance with LimbLab? You've come to the right place! This guide provides multiple ways to get help, from quick answers to detailed support.

## 🚀 Quick Start Help

### First Time User?
1. **Check the [Quick Start Guide](index.md#quick-start)** - Get up and running in minutes
2. **Follow the [Hoxa11 Tutorial](tutorials/hoxa11.md)** - Complete step-by-step example
3. **Review the [CLI Documentation](cli.md)** - Command reference with examples

---


## Getting Support

### Direct Contact

**Primary Support Email:** [laura.avino@embl.es](mailto:laura.avino@embl.es)

**What to include in your email:**

- **Subject:** Clear description of the issue
- **LimbLab version:** `limb --version`
- **Operating system:** Windows/macOS/Linux version
- **Error message:** Copy the complete error text
- **Steps to reproduce:** Detailed description of what you did
- **Expected vs. actual behavior:** What you expected vs. what happened
- **Data description:** Brief description of your data (format, size, etc.)

**Example email:**

```
Subject: Volume processing fails with large TIFF files

Hi,

I'm having trouble processing large volume files with LimbLab.

Version: 0.2.0
OS: macOS 14.0
Error: "MemoryError: Unable to allocate array"

Steps:
1. Created experiment: limb create-experiment test
2. Tried to clean volume: limb clean-volume test large_file.tif DAPI
3. Got memory error after 5 minutes

The file is 2.5GB TIFF, 2048x2048x512 pixels.
Expected: Successful processing
Actual: Memory error

Any help would be appreciated!

Thanks,
[Your name]
```

---

## Troubleshooting Guide

### Installation Help

#### Common Installation Issues

**"pip install limb fails"**
```bash
# Try upgrading pip first
pip install --upgrade pip

# Install with verbose output
pip install limb -v

# Check Python version (requires 3.8+)
python --version
```

**"ImportError: No module named 'limb'"**
```bash
# Check if installed correctly
pip list | grep limb

# Try installing in user space
pip install --user limb

# Check Python environment
which python
which pip
```

**"Permission denied" errors**
```bash
# Use virtual environment
python -m venv limblab_env
source limblab_env/bin/activate  # On Windows: limblab_env\Scripts\activate
pip install limb
```

### CLI Troubleshooting

#### Command Not Found
```bash
# Check if limb is in PATH
which limb

# Try running with python -m
python -m limb --help

# Reinstall if necessary
pip uninstall limb
pip install limb
```

#### Parameter Errors
```bash
# Check command help
limb clean-volume --help

# Verify parameter format
limb clean-volume experiment data.tif DAPI --sigma 6,6,6  # Correct
limb clean-volume experiment data.tif DAPI --sigma 6 6 6  # Wrong
```

#### File Path Issues
```bash
# Use absolute paths
limb clean-volume /full/path/to/experiment /full/path/to/data.tif DAPI

# Check file permissions
ls -la data.tif

# Verify file exists
file data.tif
```

### Quality Control

#### Poor Volume Processing Results
- **Check raw data quality:** Ensure good signal-to-noise ratio
- **Adjust parameters:** Try different sigma and cutoff values
- **Verify file format:** Ensure TIFF files are not corrupted
- **Check memory:** Large files may need more RAM

#### Surface Extraction Problems
- **Try automatic isovalue:** Use `--auto` flag
- **Manual isovalue selection:** Experiment with different values
- **Check volume quality:** Poor input = poor surface
- **Consider manual cleaning:** Use external tools if needed

#### Staging Failures
- **Place points correctly:** Along proximal-distal axis AER
- **Use enough points:** 10 points minimum recommended
- **Check surface quality:** Poor surface affects staging

---

## 📋 FAQ (Frequently Asked Questions)

### General Questions

**Q: What file formats does LimbLab support?**
A: Input: TIFF volumes (.tif, .tiff). Output: VTK surfaces (.vtk), TIFF volumes, PNG images.

**Q: How much memory do I need?**
A: Minimum 8GB, recommended 16GB+. Large volumes (>2GB) may need 32GB+.

**Q: Can I process multiple channels at once?**
A: Not yet! Process each channel separately, then visualize together with `limb vis isosurfaces experiment CHANNEL1 CHANNEL2`.

**Q: Is LimbLab free to use?**
A: Yes, LimbLab is open-source and free for academic and commercial use.

### Technical Questions

**Q: Why does my surface look noisy?**
A: Try adjusting the isovalue during surface extraction, or use the `--auto` flag for automatic selection.

**Q: Can I automate the pipeline?**
A: Yes! Use Python scripts with the API, or create shell scripts for batch processing.

**Q: What's the difference between linear and non-linear alignment?**
A: Linear: rotation/translation (faster). Non-linear: morphing (more accurate, slower).

### Scientific Questions

**Q: How accurate is the limb staging?**
A: Typically ±0.5 stages with good quality data. Accuracy depends on surface quality and point placement.

**Q: Can I compare different developmental stages?**
A: Yes! Align each limb to the appropriate reference template for comparative limb.

**Q: How do I quantify gene expression?**
A: Use the probe visualization tool to extract quantitative data from specific regions. More Gene Expression 

**Q: Can I analyze time series data?**
A: Yes! Process each time point separately, then compare aligned results.

---

## Contributing

### How to Help
- **Report bugs:** Use GitHub Issues with detailed information
- **Suggest features:** Describe your use case and requirements
- **Improve documentation:** Submit pull requests for better docs
- **Share examples:** Contribute to the examples repository
- **Answer questions:** Help other users in discussions

### Development
- **Code contributions:** Fork the repository and submit pull requests
- **Testing:** Help test new features and report issues
- **Documentation:** Improve tutorials and user guides
- **Community:** Participate in discussions and help new users

---

## Contact Information

### Primary Contact
- **Email:** [laura.avino@embl.es](mailto:laura.avino@embl.es)
- **Response time:** Usually within 24-48 hours working hours
- **Best for:** Technical support, bug reports, feature requests, say thanks! 

### Alternative Contacts
- **GitHub Issues:** [https://github.com/lauavinyo/limblab/issues](https://github.com/lauavinyo/limb/issues)
- **GitHub Discussions:** [https://github.com/lauavinyo/limblimb/discussions](https://github.com/lauavinyo/limb/discussions)
- **Community Forum:** [https://limb.org/forum](https://limb.org/forum)

---

*We're here to help! Don't hesitate to reach out if you need assistance with LimbLab. Our goal is to make 3D limb limb accessible to everyone.*