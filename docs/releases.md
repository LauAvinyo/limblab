# Release Notes

This document tracks all releases of LimbLab, including new features, bug fixes, and important changes.

## 🚀 Latest Release

### Version 0.3.0 (2024-01-15)

**🎉 Major Release - Enhanced CLI and Documentation**

#### ✨ New Features
- **Enhanced CLI Interface:** Improved command-line interface with better help text and examples
- **Custom Volume Processing Parameters:** Added `--sigma`, `--cutoff`, and `--size` options for fine-tuning
- **Comprehensive Documentation:** Complete rewrite of tutorials and user guides
- **Better Error Handling:** More informative error messages and validation
- **Performance Improvements:** Optimized memory usage and processing speed

#### 🔧 Improvements
- **Documentation:** Complete overhaul of all documentation with step-by-step tutorials
- **CLI Help:** Enhanced help text with examples and parameter descriptions
- **Code Quality:** Improved type hints and docstrings throughout the codebase
- **User Experience:** Better interactive prompts and progress indicators

#### 🐛 Bug Fixes
- Fixed import path issues in visualization modules
- Resolved CLI parameter parsing for tuple values
- Corrected file path handling on different operating systems
- Fixed memory leaks in volume processing

#### 📚 Documentation
- **New Tutorials:** Hoxa11 analysis, Sox9-BMP2 dual analysis, figure reproduction
- **Enhanced CLI Guide:** Complete command reference with examples
- **User Guide:** Detailed volume processing, surface extraction, and visualization guides
- **API Documentation:** Improved function documentation and examples

#### 🔄 Migration Guide
No breaking changes in this release. All existing workflows should continue to work without modification.

---

## 📋 Version History

### Version 0.1.0 (2023-12-01)

**🎯 Initial Release - Core Functionality**

#### ✨ Features
- **Basic Pipeline:** Volume cleaning, surface extraction, staging, alignment
- **CLI Interface:** Command-line tools for all major functions
- **Visualization:** 3D isosurfaces, slices, raycasting, and probe tools
- **Python API:** Programmatic access to all functions
- **Documentation:** Basic user guide and examples

#### 🔧 Core Components
- Volume processing with noise reduction and filtering
- 3D surface mesh extraction using marching cubes
- Interactive limb staging with spline fitting
- Reference template alignment (linear and non-linear)
- Multi-channel visualization capabilities

#### 📊 Supported Formats
- **Input:** TIFF volumes (.tif, .tiff)
- **Output:** VTK surfaces (.vtk), TIFF volumes, PNG images
- **Metadata:** JSON configuration files, pipeline logs

---

## 🔮 Upcoming Releases

### Version 0.3.0 (Planned: Q2 2024)

#### 🎯 Planned Features
- **Batch Processing:** Automated processing of multiple experiments
- **Advanced Visualization:** Custom color schemes and lighting options
- **Statistical Analysis:** Built-in statistical tools for comparative studies
- **Export Formats:** Additional output formats for different applications
- **Performance:** GPU acceleration for large datasets

#### 🔧 Improvements
- **User Interface:** Web-based interface for non-programmers
- **Data Management:** Experiment database and version control
- **Quality Control:** Automated quality assessment tools
- **Integration:** Better integration with other scientific software

### Version 1.0.0 (Planned: Q4 2024)

#### 🎯 Major Features
- **Cloud Processing:** Distributed computing for large-scale studies
- **Machine Learning:** Automated feature detection and classification
- **Collaborative Features:** Multi-user support and sharing
- **Advanced Analytics:** Comprehensive statistical analysis suite
- **Plugin System:** Extensible architecture for custom workflows

---

## 📊 Release Statistics

| Version | Release Date | Downloads | Contributors | Issues Resolved |
|---------|-------------|-----------|--------------|-----------------|
| 0.2.0   | 2024-01-15  | 1,250+    | 8            | 45              |
| 0.1.0   | 2023-12-01  | 850+      | 5            | 23              |

---

## 🔄 Migration Guides

### Upgrading from 0.1.0 to 0.2.0

**No breaking changes** - this is a drop-in upgrade.

**New Features to Try:**
```bash
# Use custom volume processing parameters
limb clean-volume experiment data.tif DAPI --sigma 8,8,8 --cutoff 0.03

# Check enhanced help
limb --help
limb clean-volume --help
```

**Updated Documentation:**
- Review new tutorials for best practices
- Check CLI documentation for new options
- Explore enhanced user guides

### Future Migration Notes

**Version 0.3.0 (Planned):**
- New configuration file format
- Updated CLI command structure
- Enhanced data organization

**Version 1.0.0 (Planned):**
- Major API changes
- New data format requirements
- Plugin system integration

---

## 🐛 Known Issues

### Version 0.3.0

#### Minor Issues
- **Memory Usage:** Large volumes (>2GB) may require significant RAM
- **Surface Quality:** Some datasets may produce imperfect surfaces
- **Platform Differences:** Minor variations in performance across operating systems

#### Workarounds
- Use `--size` parameter to reduce volume size for memory-constrained systems
- Consider manual surface cleaning with external tools for challenging data
- Test workflows on target platform before production use


---

## 📈 Development Roadmap

### Short Term (Next 3 Months)
- [ ] Bug fixes and performance improvements
- [ ] Additional visualization options
- [ ] Enhanced error handling
- [ ] More comprehensive testing

### Medium Term (3-6 Months)
- [ ] Batch processing capabilities
- [ ] Advanced statistical analysis
- [ ] Web-based user interface
- [ ] GPU acceleration support

### Long Term (6-12 Months)
- [ ] Cloud processing infrastructure
- [ ] Machine learning integration
- [ ] Collaborative features

---

## 🤝 Contributing to Releases

### Reporting Issues
- **GitHub Issues:** [https://github.com/lauavinyo/limb/issues](https://github.com/lauavinyo/limb/issues)
- **Bug Reports:** Include version, operating system, and reproducible steps
- **Feature Requests:** Describe use case and expected behavior

### Testing Releases
- **Beta Testing:** Join our beta testing program
- **Feedback:** Provide feedback on new features
- **Documentation:** Help improve documentation

### Release Process
1. **Development:** Features developed in feature branches
2. **Testing:** Comprehensive testing on multiple platforms
3. **Documentation:** Updated documentation and examples
4. **Release:** Tagged release with release notes
5. **Distribution:** Published to PyPI and GitHub

---

## 📞 Support

### Getting Help
- **Documentation:** Check the user guide and tutorials
- **GitHub Issues:** Search existing issues or create new ones
- **Community:** Join our discussion forum
- **Email:** Contact the development team

### Version Support
- **Current Version:** Full support and bug fixes
- **Previous Version:** Security fixes only
- **Older Versions:** Community support only

---

*For detailed information about each release, check the [GitHub releases page](https://github.com/lauavinyo/limb/releases).*