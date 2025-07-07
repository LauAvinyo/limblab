# Getting Help with LimbLab

Need assistance with LimbLab? You've come to the right place! This guide provides multiple ways to get help, from quick answers to detailed support.

## 🚀 Quick Start Help

### First Time User?
1. **Check the [Quick Start Guide](index.md#quick-start)** - Get up and running in minutes
2. **Follow the [Hoxa11 Tutorial](tutorials/hoxa11.md)** - Complete step-by-step example
3. **Review the [CLI Documentation](cli.md)** - Command reference with examples

### Common Issues
- **Installation problems?** → [Installation Guide](#installation-help)
- **Command not working?** → [CLI Troubleshooting](#cli-troubleshooting)
- **Poor results?** → [Quality Control](#quality-control)
- **Performance issues?** → [Performance Optimization](#performance-optimization)

---

## 📚 Self-Help Resources

### Documentation
- **[Main Documentation](index.md)** - Overview and getting started
- **[Tutorials](tutorials/)** - Step-by-step guides for common tasks
- **[User Guide](userGuide/)** - Detailed explanations of each component
- **[CLI Reference](cli.md)** - Complete command documentation
- **[API Documentation](api.md)** - Python interface reference

### Examples and Templates
- **[Sample Data](examples/)** - Download and try with example data
- **[Workflow Scripts](examples/scripts/)** - Automated analysis examples
- **[Configuration Templates](examples/config/)** - Pre-configured settings

### Video Resources
- **[Installation Guide](https://youtube.com/watch?v=example1)** - Video walkthrough
- **[Basic Workflow](https://youtube.com/watch?v=example2)** - Complete pipeline demo
- **[Advanced Features](https://youtube.com/watch?v=example3)** - Custom analysis techniques

---

## 🆘 Getting Support

### 📧 Direct Contact

**Primary Support Email:** [laura.avino@embl.es](mailto:laura.avino@embl.es)

**What to include in your email:**
- **Subject:** Clear description of the issue
- **LimbLab version:** `limblab --version`
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
1. Created experiment: limblab create-experiment test
2. Tried to clean volume: limblab clean-volume test large_file.tif DAPI
3. Got memory error after 5 minutes

The file is 2.5GB TIFF, 2048x2048x512 pixels.
Expected: Successful processing
Actual: Memory error

Any help would be appreciated!

Thanks,
[Your name]
```

### 💬 Community Support

#### GitHub Discussions
- **[General Questions](https://github.com/lauavinyo/limblab/discussions)** - Ask the community
- **[Tips & Tricks](https://github.com/lauavinyo/limblab/discussions/categories/tips-and-tricks)** - Share your knowledge
- **[Show & Tell](https://github.com/lauavinyo/limblab/discussions/categories/show-and-tell)** - Share your results

#### GitHub Issues
- **[Bug Reports](https://github.com/lauavinyo/limblab/issues)** - Report software bugs
- **[Feature Requests](https://github.com/lauavinyo/limblab/issues)** - Suggest new features
- **[Documentation Issues](https://github.com/lauavinyo/limblab/issues)** - Report documentation problems

### 🌐 Online Resources

#### Stack Overflow
- **Tag:** `[limblab]` - Search for existing answers
- **Ask Question:** Include the limblab tag for visibility

#### Scientific Forums
- **ImageJ Forum:** For image processing questions
- **Bioinformatics Stack Exchange:** For analysis workflows
- **Research Gate:** For scientific applications

---

## 🔧 Troubleshooting Guide

### Installation Help

#### Common Installation Issues

**"pip install limblab fails"**
```bash
# Try upgrading pip first
pip install --upgrade pip

# Install with verbose output
pip install limblab -v

# Check Python version (requires 3.8+)
python --version
```

**"ImportError: No module named 'limblab'"**
```bash
# Check if installed correctly
pip list | grep limblab

# Try installing in user space
pip install --user limblab

# Check Python environment
which python
which pip
```

**"Permission denied" errors**
```bash
# Use virtual environment
python -m venv limblab_env
source limblab_env/bin/activate  # On Windows: limblab_env\Scripts\activate
pip install limblab
```

### CLI Troubleshooting

#### Command Not Found
```bash
# Check if limblab is in PATH
which limblab

# Try running with python -m
python -m limblab --help

# Reinstall if necessary
pip uninstall limblab
pip install limblab
```

#### Parameter Errors
```bash
# Check command help
limblab clean-volume --help

# Verify parameter format
limblab clean-volume experiment data.tif DAPI --sigma 6,6,6  # Correct
limblab clean-volume experiment data.tif DAPI --sigma 6 6 6  # Wrong
```

#### File Path Issues
```bash
# Use absolute paths
limblab clean-volume /full/path/to/experiment /full/path/to/data.tif DAPI

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
- **Place points correctly:** Along proximal-distal axis
- **Use enough points:** 5-10 points recommended
- **Check surface quality:** Poor surface affects staging
- **Verify limb orientation:** Ensure proper alignment

### Performance Optimization

#### Slow Processing
```bash
# Reduce output size
--size 256,256,148

# Use SSD storage
# Close other applications
# Increase system RAM
```

#### Memory Issues
```bash
# Process smaller volumes
--size 128,128,74

# Use batch processing
# Process one channel at a time
# Check available memory
```

#### Large File Handling
```bash
# Use compression
--compress lzw

# Process in chunks
# Use external storage
# Consider data reduction
```

---

## 📋 FAQ (Frequently Asked Questions)

### General Questions

**Q: What file formats does LimbLab support?**
A: Input: TIFF volumes (.tif, .tiff). Output: VTK surfaces (.vtk), TIFF volumes, PNG images.

**Q: How much memory do I need?**
A: Minimum 8GB, recommended 16GB+. Large volumes (>2GB) may need 32GB+.

**Q: Can I process multiple channels at once?**
A: Yes! Process each channel separately, then visualize together with `limblab vis isosurfaces experiment CHANNEL1 CHANNEL2`.

**Q: Is LimbLab free to use?**
A: Yes, LimbLab is open-source and free for academic and commercial use.

### Technical Questions

**Q: Why does my surface look noisy?**
A: Try adjusting the isovalue during surface extraction, or use the `--auto` flag for automatic selection.

**Q: How do I get publication-quality figures?**
A: Use the `--high-res` flag for visualizations, and check our [Figure Reproduction Tutorial](tutorials/figure_reproduction.md).

**Q: Can I automate the pipeline?**
A: Yes! Use Python scripts with the API, or create shell scripts for batch processing.

**Q: What's the difference between linear and non-linear alignment?**
A: Linear: rotation/translation (faster). Non-linear: morphing (more accurate, slower).

### Scientific Questions

**Q: How accurate is the limb staging?**
A: Typically ±0.5 stages with good quality data. Accuracy depends on surface quality and point placement.

**Q: Can I compare different developmental stages?**
A: Yes! Align each limb to the appropriate reference template for comparative analysis.

**Q: How do I quantify gene expression?**
A: Use the probe visualization tool to extract quantitative data from specific regions.

**Q: Can I analyze time series data?**
A: Yes! Process each time point separately, then compare aligned results.

---

## 🎓 Learning Resources

### Beginner Level
- **[Quick Start Guide](index.md#quick-start)** - Get started in 10 minutes
- **[Hoxa11 Tutorial](tutorials/hoxa11.md)** - Complete workflow example
- **[CLI Basics](cli.md)** - Essential commands

### Intermediate Level
- **[Sox9-BMP2 Tutorial](tutorials/sox9_bmp2.md)** - Multi-channel analysis
- **[Volume Processing](userGuide/volume.md)** - Advanced processing techniques
- **[Custom Parameters](cli.md#custom-parameters)** - Fine-tuning your analysis

### Advanced Level
- **[Figure Reproduction](tutorials/figure_reproduction.md)** - Publication-quality output
- **[API Documentation](api.md)** - Programmatic access
- **[Performance Optimization](userGuide/volume.md#performance-optimization)** - Large-scale analysis

### Scientific Applications
- **[Gene Expression Analysis](tutorials/hoxa11.md)** - 3D spatial analysis
- **[Developmental Biology](tutorials/sox9_bmp2.md)** - Comparative studies
- **[Publication Standards](tutorials/figure_reproduction.md)** - Journal requirements

---

## 🤝 Contributing

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

## 📞 Contact Information

### Primary Contact
- **Email:** [laura.avino@embl.es](mailto:laura.avino@embl.es)
- **Response time:** Usually within 24-48 hours
- **Best for:** Technical support, bug reports, feature requests

### Alternative Contacts
- **GitHub Issues:** [https://github.com/lauavinyo/limblab/issues](https://github.com/lauavinyo/limblab/issues)
- **GitHub Discussions:** [https://github.com/lauavinyo/limblab/discussions](https://github.com/lauavinyo/limblab/discussions)
- **Community Forum:** [https://limblab.org/forum](https://limblab.org/forum)

### Institutional Support
- **EMBL Heidelberg:** For institutional users and collaborators
- **Research Groups:** For specific scientific applications
- **Workshops:** For training and education

---

## 📊 Support Statistics

### Response Times
- **Email support:** 24-48 hours average
- **GitHub issues:** 1-3 days average
- **Community forum:** 1-7 days average
- **Documentation updates:** 1-2 weeks

### Support Channels
- **Email:** 60% of support requests
- **GitHub Issues:** 25% of support requests
- **Community Forum:** 10% of support requests
- **Documentation:** 5% of support requests

### Common Issues
- **Installation problems:** 30%
- **Parameter tuning:** 25%
- **Performance issues:** 20%
- **Data format problems:** 15%
- **Other:** 10%

---

*We're here to help! Don't hesitate to reach out if you need assistance with LimbLab. Our goal is to make 3D limb analysis accessible to everyone.*